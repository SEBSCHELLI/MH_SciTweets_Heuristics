import ast
import requests
import sys
import tldextract
import pandas as pd

subdomains = pd.read_csv('repo_subdomains.csv')['domain'].values
sci_mags_domains = pd.read_csv('science_mags_domains.csv')['domain'].values
sci_news_domains = pd.read_csv('news_outlets_domains.csv')['domain'].values


def url2domain(url):
    """Extract the domain from URL.
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
        return url, res.suffix, ".".join(domain_parts), ".".join(subdomain_parts)
    else:
        return url, "error", "error", "error"


def prepare_urls(tweets):
    # split tweets into tweets with url and tweets without url
    tweets['urls'] = tweets['urls'].apply(lambda urls: ast.literal_eval(urls))
    tweets_w_url = tweets[tweets['urls'].apply(lambda x: len(x) > 0)].copy()
    tweets_wo_url = tweets[tweets['urls'].apply(lambda x: len(x) == 0)].copy()

    # annotate if a tweet contains a url
    tweets_w_url['has_url'] = True
    tweets_wo_url['has_url'] = False

    # for tweets with url, explode tweets with multiple urls to multiple rows
    tweets_w_url = tweets_w_url.explode("urls").reset_index(drop=True)
    tweets_w_url = tweets_w_url[tweets_w_url["urls"] != ""]
    tweets_w_url = tweets_w_url.rename(columns={'urls': 'url'})

    # for tweets with url, annotate each url with tld, domain and subdomain
    res = tweets_w_url['url'].apply(url2domain)
    res = list(map(list, zip(*res.values)))
    tweets_w_url["processed_url"] = res[0]
    tweets_w_url["tld"] = res[1]
    tweets_w_url["tld"] = tweets_w_url["tld"].str.lower()
    tweets_w_url["domain_tld"] = res[2]
    tweets_w_url["domain_tld"] = tweets_w_url["domain_tld"].str.lower()
    tweets_w_url["subdomain_domain_tld"] = res[3]
    tweets_w_url["subdomain_domain_tld"] = tweets_w_url["subdomain_domain_tld"].str.lower()

    # for tweets with url, group tweets with multiple urls to back to single row
    cols = tweets_w_url.columns.tolist()
    cols = [col for col in cols if col not in ['url', 'processed_url', 'tld', 'domain_tld', 'subdomain_domain_tld']]
    tweets_w_url = (tweets_w_url.groupby(by=cols, dropna=False)
                    .agg({'url': lambda x: x.tolist(),
                          'processed_url': lambda x: x.tolist(),
                          'tld': lambda x: x.tolist(),
                          'domain_tld': lambda x: x.tolist(),
                          'subdomain_domain_tld': lambda x: x.tolist()
                          })
                    .rename(columns={'url': 'urls',
                                     'processed_url': 'processed_urls',
                                     'tld': 'tlds',
                                     'domain_tld': 'domain_tlds',
                                     'subdomain_domain_tld': 'subdomain_domain_tlds'
                                     })
                    .reset_index())

    # fill empty fields for tweets without urls
    tweets_wo_url["urls"] = [[]] * len(tweets_wo_url)
    tweets_wo_url["processed_urls"] = [[]] * len(tweets_wo_url)
    tweets_wo_url["tlds"] = [[]] * len(tweets_wo_url)
    tweets_wo_url["domain_tlds"] = [[]] * len(tweets_wo_url)
    tweets_wo_url["subdomain_domain_tlds"] = [[]] * len(tweets_wo_url)

    tweets = pd.concat([tweets_w_url, tweets_wo_url])
    return tweets


def annotate_sci_crossref_subdomains(domains):
    matches = []

    for domain in domains:
        for sci_domain in subdomains:
            if sci_domain in domain:
                if domain == sci_domain:
                    matches.append(domain)
                # check if subdomain is below sci_subdomain
                elif domain.endswith('.' + sci_domain):
                    matches.append(domain)

    return "; ".join(matches)


def annotate_sci_mag_domains(domains):
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
    tweets_w_url = tweets[tweets['has_url']].copy()
    tweets_wo_url = tweets[~tweets['has_url']].copy()

    # check if tweet subdomains are science-related
    tweets_w_url['sci_subdomain'] = tweets_w_url['subdomain_domain_tlds'].apply(annotate_sci_crossref_subdomains)
    tweets_w_url["has_sci_subdomain"] = tweets_w_url['sci_subdomain'].apply(lambda x: True if len(x) > 0 else False)

    tweets_wo_url['sci_subdomain'] = tweets_wo_url['has_url'].apply(lambda x: [])
    tweets_wo_url["has_sci_subdomain"] = False

    tweets_w_url['sci_mag_domain'] = tweets_w_url['subdomain_domain_tlds'].apply(annotate_sci_mag_domains)
    tweets_w_url["has_sci_mag_domain"] = tweets_w_url['sci_mag_domain'].apply(lambda x: True if len(x) > 0 else False)

    tweets_wo_url['sci_mag_domain'] = tweets_wo_url['has_url'].apply(lambda x: [])
    tweets_wo_url["has_sci_mag_domain"] = False

    tweets_w_url['sci_news_domain'] = tweets_w_url[['subdomain_domain_tlds', 'processed_urls']].apply(
        lambda x: annotate_sci_news_domains(x["subdomain_domain_tlds"], x["processed_urls"]), axis=1)
    tweets_w_url["has_sci_news_domain"] = tweets_w_url['sci_news_domain'].apply(lambda x: True if len(x) > 0 else False)

    tweets_wo_url['sci_news_domain'] = tweets_wo_url['has_url'].apply(lambda x: [])
    tweets_wo_url["has_sci_news_domain"] = False

    tweets = pd.concat([tweets_w_url, tweets_wo_url], ignore_index=True)
    del tweets["processed_urls"]
    del tweets["tlds"]
    del tweets["domain_tlds"]
    del tweets["subdomain_domain_tlds"]
    del tweets["has_url"]
    return tweets


if __name__ == '__main__':
    tweet_data_path = sys.argv[1]
    tweet_data = pd.read_csv(tweet_data_path, sep='\t')

    print('prepare tweets with urls (extract subdomains)')
    tweet_data = prepare_urls(tweet_data)

    print('run heuristics')
    tweet_data = annotate_tweets(tweet_data)

    tweet_data['is_cat2'] = tweet_data[['has_sci_subdomain', 'has_sci_mag_domain', 'has_sci_news_domain']].any(
        axis='columns')

    tweet_data.to_csv(tweet_data_path.replace(".tsv", "_cat2_heuristics.tsv"), sep="\t", index=False)