import en_core_web_sm
import re
import sys
import pandas as pd
from nltk.tokenize import sent_tokenize
nlp = en_core_web_sm.load()

with open('sc_methods.txt') as f:
    methods = f.read().splitlines()

exclude_methods = ['life story', 'sample size', 'ideal type', 'life experiences', 'data privacy', 'role playing', 'data quality', 'survey results', 'research grants', 'false negative']
methods = [method for method in methods if method not in exclude_methods]


def mentions_scientist(tweet_sentence):
    scientists = ["research team", "research group", "scientist", "researcher", "psychologist", "chemist", "physician", "biologist", "economist", "engineer", "physicist", "geologist"]
    for term in scientists:
        res = re.search('\s('+term+')s?\s', tweet_sentence)
        if res is not None:
            doc = nlp(tweet_sentence)
            for token in doc:
                if token.pos_ in ["NOUN", "PROPN"]:
                    if token.text == term or token.text == term.split(" ")[0]:
                        return term
    return ""


def mentions_science_research_in_general(tweet_sentence):
    science_research_in_general = ['research on', 'research in', 'research for', 'research from', 'research of', 'research to', 'research at', 'research by', 'research', 'science of', 'science to', 'science', 'sciences of', 'sciences to', 'sciences']
    for term in science_research_in_general:
        res = re.search('\s('+term+')s?\s[a-zA-Z]*',tweet_sentence)
        if res is not None:
            doc = nlp(tweet_sentence)
            for token in doc:
                if token.pos_ in ["NOUN", "PROPN"]:
                    if token.text == term or token.text == term.split(" ")[0]:
                        return term
    return ""


def mentions_research_method(tweet_sentence):
    for term in methods:
        if " " in term:
            if " " + term + " " in tweet_sentence:
                return term

    return ""

def mentions_discovery(tweet_sentence):
    discovery_verbs = ["predict", "discover", "say", "find", "show", "develop", "research", "highlight", "constitute", "suggest", "indicate", "demonstrate", "show", "reveal", "provide", "illustrate", "describe", "conclude", "support", "establish", "propose", "advocate", "determine", "confirm", "argue", "impl", "display", "offer", "underline", "allow"]

    scientists = mentions_scientist(tweet_sentence)
    science_research = ""
    if scientists == "":
        science_research = mentions_science_research_in_general(tweet_sentence)

    scientists_science_research = scientists + science_research

    if scientists_science_research != "":
        doc = nlp(tweet_sentence)
        for token in doc:
            if token.pos_ == "VERB":
                if token.lemma_ in discovery_verbs:
                    return scientists_science_research +" + "+token.lemma_

    return ""

def mentions_publications(tweet_sentence):
    science_research_in_general = ['publications', 'posters', 'reports', 'statistics', 'datasets', 'findings', 'papers', 'studies', 'experiments', 'surveys']
    for term in science_research_in_general:
        res = re.search('\s(' + term + ')s?\s[a-zA-Z]*', tweet_sentence)
        if res is not None:
            doc = nlp(tweet_sentence)
            for token in doc:
                if token.pos_ in ["NOUN", "PROPN"]:
                    if token.text == term or token.text == term.split(" ")[0]:
                        return term
    return ""


def is_related_to_research(tweet):
    tweet = tweet.lower()
    sentences = sent_tokenize(tweet)
    for sent in sentences:

        msrig = mentions_science_research_in_general(sent)
        ms = mentions_scientist(sent)
        mp = mentions_publications(sent)
        mrm = mentions_research_method(sent)

    return msrig, ms, mp, mrm


def annotate_tweets(tweets):
    res = tweets['text'].apply(is_related_to_research)
    res = list(map(list, zip(*res.values)))
    tweets["mentions_science_research_in_general"] = res[0]
    tweets["mentions_scientist"] = res[1]
    tweets["mentions_publications"] = res[2]
    tweets["mentions_research_method"] = res[3]
    return tweets


if __name__ == '__main__':
    tweet_data_path = sys.argv[1]
    tweet_data = pd.read_csv(tweet_data_path, sep='\t')

    print('run heuristics')
    tweet_data = annotate_tweets(tweet_data)

    tweet_data['is_cat3'] = tweet_data[['mentions_science_research_in_general', 'mentions_scientist', 'mentions_publications', 'mentions_research_method']].any(axis='columns')

    tweet_data.to_csv(tweet_data_path.replace(".tsv", "_cat3_heuristics.tsv"), sep="\t", index=False)