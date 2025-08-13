import argparse
import ast
import tldextract
import pandas as pd

# Load lists of relevant subdomains
repo_subdomains = pd.read_csv('heuristics/repo_subdomains.csv')['domain'].values
sci_mags_domains = pd.read_csv('heuristics/science_mags_domains.csv')['domain'].values
sci_news_domains = pd.read_csv('heuristics/news_outlets_domains.csv')['domain'].values


def url2domain(url):
    """
    Extracts domain from a given URL using `tldextract`.

    Parameters:
        url (str): The input URL as a string.

    Returns:
        str: Full domain with subdomain (e.g., 'www.nytimes.com'), "error" if extraction fails.
    """
    url = str(url)
    res = tldextract.extract(url)

    domain_parts = []
    subdomain_parts = []

    if res.domain != '':
        domain_parts.append(res.domain)

    if res.suffix != '':
        domain_parts.append(res.suffix)

    if res.subdomain != '':
        subdomain_parts.append(res.subdomain)

    subdomain_parts.extend(domain_parts)

    if len(domain_parts) >= 2:
        return ".".join(subdomain_parts)
    else:
        return "error"


def prepare_urls(tweets):
    """
    Process tweets DataFrame and extract domains.

    Parameters:
        tweets (pd.DataFrame): The input DataFrame

    Returns:
        pd.DataFrame: tweets DataFrame with additional columns for extracted domains and if tweet contains a URL.
    """
    # split tweets into tweets with url and tweets without url
    tweets['urls'] = tweets['urls'].apply(lambda urls: ast.literal_eval(urls))
    tweets_w_url = tweets[tweets['urls'].apply(lambda x: len(x) > 0)].copy()
    tweets_wo_url = tweets[tweets['urls'].apply(lambda x: len(x) == 0)].copy()

    # annotate if a tweet contains an url
    tweets_w_url['has_url'] = True
    tweets_wo_url['has_url'] = False

    # for tweets with url, explode tweets with multiple urls to multiple rows
    tweets_w_url = tweets_w_url.explode("urls").reset_index(drop=True)
    tweets_w_url = tweets_w_url[tweets_w_url["urls"] != ""]
    tweets_w_url = tweets_w_url.rename(columns={'urls': 'url'})

    # for tweets with url, annotate each url with tld, domain and subdomain
    tweets_w_url["domain"] = tweets_w_url['url'].apply(url2domain)
    tweets_w_url["domain"] = tweets_w_url["domain"].str.lower()

    # for tweets with url, group tweets with multiple urls to back to single row
    cols = tweets_w_url.columns.tolist()
    cols = [col for col in cols if col != 'domain']
    tweets_w_url = (tweets_w_url.groupby(by=cols, dropna=False)
                    .agg({'domain': lambda x: x.tolist(),
                          'url': lambda x: x.tolist()})
                    .rename(columns={'domain': 'domains',
                                     'url': 'urls'})
                    .reset_index())

    del tweets_w_url["url"]

    # fill empty fields for tweets without urls
    tweets_wo_url["domains"] = [[]] * len(tweets_wo_url)

    tweets = pd.concat([tweets_w_url, tweets_wo_url])
    return tweets


def annotate_sci_crossref_subdomains(domains):
    """
    Annotates a list of domains by checking which ones match known scientific subdomains.

    A domain is considered a match if it:
      - exactly matches a known scientific subdomain, or
      - is a subdomain of one (e.g., 'data.nature.com' matches 'nature.com').

    Parameters:
        domains (list of str): List of domain strings to check.

    Returns:
        str: A semicolon-separated string of matched domains.
    """
    matches = []

    for domain in domains:
        for sci_domain in repo_subdomains:
            if sci_domain in domain:
                if domain == sci_domain:
                    matches.append(domain)
                # check if subdomain is below sci_subdomain
                elif domain.endswith('.' + sci_domain):
                    matches.append(domain)

    return "; ".join(matches)


def annotate_sci_mag_domains(domains):
    """
    Annotates a list of domains by checking which ones match known scientific magazine subdomains.

    A domain is considered a match if it:
      - exactly matches a known scientific magazine subdomain, or
      - is a subdomain of one (e.g., 'data.nature.com' matches 'nature.com').

    Parameters:
        domains (list of str): List of domain strings to check.

    Returns:
        str: A semicolon-separated string of matched domains.
    """
    matches = []

    for domain in domains:
        for sci_domain in sci_mags_domains:
            if sci_domain in domain:
                if domain == sci_domain:
                    matches.append(domain)
                # check if subdomain is below sci_subdomain
                elif domain.endswith('.' + sci_domain):
                    matches.append(domain)

    return "; ".join(matches)


def annotate_sci_news_domains(domains, urls):
    """
    Annotates domains as science-related news sources if:
      - The URL contains the '/science' path, and
      - The domain matches or is a subdomain of a known science news domain.

    Parameters:
        domains (list of str): List of domain strings.
        urls (list of str): List of corresponding URLs.

    Returns:
        str: A semicolon-separated string of matched domains.
    """
    matches = []

    for domain, url in zip(domains, urls):
        if "/science" in url:
            for sci_domain in sci_news_domains:
                if sci_domain in domain:
                    if domain == sci_domain:
                        matches.append(domain)
                    # check if subdomain is below sci_subdomain
                    elif domain.endswith('.' + sci_domain):
                        matches.append(domain)

    return "; ".join(matches)


def annotate_tweets(tweets):
    """
    Annotates a DataFrame of tweets with Category 2 (Cat2) heuristic features:

    Adds the following columns:
        - sci_subdomain / has_sci_subdomain: Matches against scientific repository subdomains
        - sci_mag_domain / has_sci_mag_domain: Matches against science magazine domains
        - sci_news_domain / has_sci_news_domain: Matches against science news outlet domains

    Parameters:
        tweets (pd.DataFrame): DataFrame containing at least 'has_url', 'domains', and 'urls' columns.

    Returns:
        pd.DataFrame: Annotated DataFrame with additional heuristic columns.
    """
    tweets_w_url = tweets[tweets['has_url']].copy()
    tweets_wo_url = tweets[~tweets['has_url']].copy()

    # check if tweet subdomains are science-related
    tweets_w_url['sci_subdomain'] = tweets_w_url['domains'].apply(annotate_sci_crossref_subdomains)
    tweets_w_url["has_sci_subdomain"] = tweets_w_url['sci_subdomain'].apply(lambda x: True if len(x) > 0 else False)

    tweets_wo_url['sci_subdomain'] = tweets_wo_url['has_url'].apply(lambda x: [])
    tweets_wo_url["has_sci_subdomain"] = False

    tweets_w_url['sci_mag_domain'] = tweets_w_url['domains'].apply(annotate_sci_mag_domains)
    tweets_w_url["has_sci_mag_domain"] = tweets_w_url['sci_mag_domain'].apply(lambda x: True if len(x) > 0 else False)

    tweets_wo_url['sci_mag_domain'] = tweets_wo_url['has_url'].apply(lambda x: [])
    tweets_wo_url["has_sci_mag_domain"] = False

    tweets_w_url['sci_news_domain'] = tweets_w_url[['domains', 'urls']].apply(lambda x: annotate_sci_news_domains(x["domains"], x["urls"]), axis=1)
    tweets_w_url["has_sci_news_domain"] = tweets_w_url['sci_news_domain'].apply(lambda x: True if len(x) > 0 else False)

    tweets_wo_url['sci_news_domain'] = tweets_wo_url['has_url'].apply(lambda x: [])
    tweets_wo_url["has_sci_news_domain"] = False

    tweets = pd.concat([tweets_w_url, tweets_wo_url], ignore_index=True)
    del tweets["domains"]
    del tweets["has_url"]

    tweets['is_cat2'] = tweets[['has_sci_subdomain', 'has_sci_mag_domain', 'has_sci_news_domain']].any(axis='columns')

    return tweets


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Load tweet data from a TSV file.")
    parser.add_argument('tweet_data_path', type=str, help='Path to the input tweet data TSV file')

    args = parser.parse_args()

    tweet_data = pd.read_csv(args.tweet_data_path, sep='\t')

    print('Prepare Tweets: Extract URL domains')
    tweet_data = prepare_urls(tweet_data)

    print('Run heuristics for category 1.2')
    tweet_data = annotate_tweets(tweet_data)

    tweet_data.to_csv(args.tweet_data_path.replace(".tsv", "_cat2_heuristics.tsv"), sep="\t", index=False)
