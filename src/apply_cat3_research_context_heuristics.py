import argparse
import en_core_web_sm
import re
import pandas as pd
import os

nlp = en_core_web_sm.load()

def load_list(filename):
    lists_directory = os.path.join(os.path.dirname(__file__), 'lists')
    with open(os.path.join(lists_directory, filename), 'r') as f:
        return [line.strip() for line in f]

methods_kws = [method for method in load_list('sc_methods.txt') if method not in load_list('exclude_methods.txt')]

scientists_kws = load_list('scientists_kws.txt')
science_research_in_general_kws = load_list('science_research_in_general_kws.txt')
discovery_verbs_kws = load_list('discovery_verbs_kws.txt')
publications_kws = load_list('publications_kws.txt')


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
        res = re.search('\\s('+term+')s?\\s[a-zA-Z]*',tweet)
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
        res = re.search('\\s('+term+')s?\\s', tweet)
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
        res = re.search('\\s(' + term + ')s?\\s[a-zA-Z]*', tweet)
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
    parser = argparse.ArgumentParser(description="Load data from a TSV file.")
    parser.add_argument('data_path', type=str, help='Path to the input data TSV file')

    args = parser.parse_args()

    data = pd.read_csv(args.data_path, sep='\t')

    print('Run heuristics for category 1.3')
    data = annotate_tweets(data)

    data.to_csv(args.data_path.replace(".tsv", "_cat3.tsv"), sep="\t", index=False)
