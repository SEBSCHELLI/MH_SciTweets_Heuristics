import argparse
import en_core_web_sm
import re
import pandas as pd
nlp = en_core_web_sm.load()


# Load lists of keywords
with open('heuristics/sc_methods.txt') as f:
    methods = f.read().splitlines()
exclude_methods = ['life story', 'sample size', 'ideal type', 'life experiences', 'data privacy', 'role playing', 'data quality', 'survey results', 'research grants', 'false negative']
methods_kws = [method for method in methods if method not in exclude_methods]

scientists_kws = ["research team", "research group", "scientist", "researcher", "psychologist", "chemist", "physician", "biologist", "economist", "engineer", "physicist", "geologist"]
science_research_in_general_kws = ['research on', 'research in', 'research for', 'research from', 'research of', 'research to', 'research at', 'research by', 'research', 'science of',
                               'science to', 'science', 'sciences of', 'sciences to', 'sciences']
discovery_verbs_kws = ["predict", "discover", "say", "find", "show", "develop", "research", "highlight", "constitute", "suggest", "indicate", "demonstrate", "show", "reveal",
                   "provide", "illustrate", "describe", "conclude", "support", "establish", "propose", "advocate", "determine", "confirm", "argue", "impl", "display", "offer",
                   "underline", "allow"]
publications_kws = ['publications', 'posters', 'reports', 'statistics', 'datasets', 'findings', 'papers', 'studies', 'experiments', 'surveys']


# Define functions for the heuristics
def mentions_science_research_in_general(tweet):
    """
    Checks whether a tweet mentions general science or research-related terms, and confirms the term appears as a noun/proper noun using spaCy's POS tagging.

    Parameters:
        tweet (str): The tweet text.

    Returns:
        str: The matched keyword if found and used as a noun; otherwise, an empty string.
    """
    for term in science_research_in_general_kws:
        res = re.search('\s('+term+')s?\s[a-zA-Z]*',tweet)
        if res is not None:
            doc = nlp(tweet)
            for token in doc:
                if token.pos_ in ["NOUN", "PROPN"]:
                    if token.text == term or token.text == term.split(" ")[0]:
                        return term
    return ""


def mentions_scientist(tweet):
    """
    Checks if a tweet mentions a scientist-related keyword, and validates that it appears as a noun/proper noun using spaCy's POS tagging.

    Parameters:
        tweet (str): The tweet text.

    Returns:
        str: The matched scientist keyword if found; otherwise, an empty string.
    """
    for term in scientists_kws:
        res = re.search('\s('+term+')s?\s', tweet)
        if res is not None:
            doc = nlp(tweet)
            for token in doc:
                if token.pos_ in ["NOUN", "PROPN"]:
                    if token.text == term or token.text == term.split(" ")[0]:
                        return term
    return ""


def mentions_publications(tweet):
    """
    Checks if a tweet mentions a publication-related keyword, and validates that it appears as a noun/proper noun using spaCy's POS tagging.

    Parameters:
        tweet (str): The tweet text.

    Returns:
        str: The matched publication keyword if found; otherwise, an empty string.
    """
    for term in publications_kws:
        res = re.search('\s(' + term + ')s?\s[a-zA-Z]*', tweet)
        if res is not None:
            doc = nlp(tweet)
            for token in doc:
                if token.pos_ in ["NOUN", "PROPN"]:
                    if token.text == term or token.text == term.split(" ")[0]:
                        return term
    return ""


def mentions_research_method(tweet):
    """
    Checks if the tweet mentions any method keyword.

    Parameters:
        tweet (str): The tweet text.

    Returns:
        str: The matched method keyword if found; otherwise, an empty string.
    """
    for term in methods_kws:
        if " " in term:
            if " " + term + " " in tweet:
                return term
    return ""


def annotate_tweets(tweets):
    """
    Annotate tweets with category 3 heuristics based on keyword detection.

    Adds columns:
        - mentions_science_research_in_general
        - mentions_scientist
        - mentions_publications
        - mentions_research_method
        - is_cat3: True if any of the above mentions exist

    Parameters:
        tweets (pd.DataFrame): DataFrame with a 'text' column containing tweet texts.

    Returns:
        pd.DataFrame: DataFrame with new columns for the heuristics added.
    """
    tweets["mentions_science_research_in_general"] = tweets['text'].apply(lambda x: mentions_science_research_in_general(x.lower()))
    tweets["mentions_scientist"] = tweets['text'].apply(lambda x: mentions_scientist(x.lower()))
    tweets["mentions_publications"] = tweets['text'].apply(lambda x: mentions_publications(x.lower()))
    tweets["mentions_research_method"] = tweets['text'].apply(lambda x: mentions_research_method(x.lower()))

    tweets['is_cat3'] = tweets[['mentions_science_research_in_general', 'mentions_scientist', 'mentions_publications', 'mentions_research_method']].any(axis='columns')

    return tweets


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Load tweet data from a TSV file.")
    parser.add_argument('tweet_data_path', type=str, help='Path to the input tweet data TSV file')

    args = parser.parse_args()

    tweet_data = pd.read_csv(args.tweet_data_path, sep='\t')

    print('Run heuristics for category 1.3')
    tweet_data = annotate_tweets(tweet_data)

    tweet_data.to_csv(args.tweet_data_path.replace(".tsv", "_cat3_heuristics.tsv"), sep="\t", index=False)
