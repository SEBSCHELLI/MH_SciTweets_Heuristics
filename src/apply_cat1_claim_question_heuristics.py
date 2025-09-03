import argparse
import en_core_web_sm
import re
import pandas as pd
import os
from nltk.tokenize import sent_tokenize, word_tokenize
nlp = en_core_web_sm.load()

import nltk
nltk.download('punkt')

def load_list(filename):
    lists_directory = os.path.join(os.path.dirname(__file__), 'lists')
    with open(os.path.join(lists_directory, filename), 'r') as f:
        return [line.strip() for line in f]

predicates = load_list('predicates.txt')

scientific_terms = [
        term for term in load_list('wiki_sci_terms.txt') + load_list('sc_methods.txt')
        if term not in (
            # Text speak words like "lol" are filtered out of the scientific terms list
            load_list('text_speak_words.txt')
            # 500 false scientific words are filtered out from the scientific terms list,
            # by a process of using the sciterm heuristic and looking at the most frequent words
            + load_list('false_scientific_words.txt'))
    ]
scientific_terms.sort()

# HEURISTIC 1: IS CLAIM (PATTERN-MATCHING: NOUN + PRED + (NOUN OR ADJ) where PRED = a predicate from the list of predicates)

# Helper function: Check if a tweet sentence contains an argumentative relation using a list of known argumentative predicates.
def contains_arg_relation(tweet_sentence):
    """
    Checks whether the given tweet sentence contains any argumentative predicate
    from the 'predicates' list using a regex pattern.

    Parameters:
        tweet_sentence (str): The text of the tweet sentence.

    Returns:
        str: The first matched predicate if found, otherwise an empty string.
    """
    for pred in predicates:
        pattern = rf"\b{re.escape(pred)}\b\s+.{{2,}}"
        if re.search(pattern, tweet_sentence):
            return pred
    return ""


def is_claim(tweet):
    """
    Checks whether the given tweet is a claim with a pattern NOUN + PRED + (NOUN OR ADJ)

    Parameters:
        tweet (str): The text of the tweet.

    Returns:
        tuple: (True, first sentence of the tweet in which a scientific claim was found), otherwise (False, "").
    """
    tweet = tweet.lower()
    pred = contains_arg_relation(tweet)
    if pred != "":
        sentences = sent_tokenize(tweet)

        for sent in sentences:
            doc = nlp(sent)

            if " "+pred+" " in sent:
                tags = [token.tag_ for token in doc]
                poss = [token.pos_ for token in doc]
                ents = [token.ent_type_ for token in doc]
                texts = [token.lower_ for token in doc]

                if len(pred.split(" ")) > 1:
                    pred_index = texts.index(pred.split(" ")[0])
                else:
                    pred_index = texts.index(pred)

                tags_before = tags[:pred_index]
                poss_before = poss[:pred_index]
                ents_before = ents[:pred_index]

                tags_after = tags[pred_index+1:]
                poss_after = poss[pred_index+1:]
                ents_after = ents[pred_index+1:]

                # Looked for pattern = NOUN + PRED + (NOUN OR ADJ)
                # Condition = what's before the predicate IS a noun AND IS NOT one of the following: personal pronoun, possessive pronoun, person including fictional
                if 'PRP' not in tags_before and 'PRP$' not in tags_before and 'PERSON' not in ents_before and 'NOUN' in poss_before:
                    # Same condition for what's after the predicate
                    if 'PRP' not in tags_after and 'PRP$' not in tags_after and 'PERSON' not in ents_after and ('NOUN' or 'ADJ' in poss_after):
                        if "?" in sent:
                            if " how " in sent or "when " in sent or "why " in sent:
                                return True, sent
                            else:
                                return True, sent
                        else:
                            return True, sent

    return False, ""


# HEURISTIC 2: CONTAINS SCIENTIFIC TERM (using scientific_terms list)
def contains_scientific_term(tweet_sentence):
    """
    Determines whether a tweet sentence contains any scientific terms from the predefined 'scientific_terms' list.

    Parameters:
        tweet_sentence (str): The text of the tweet sentence.

    Returns:
        tuple: (True, [list of found scientific terms]) if any are found, otherwise (False, []).
    """
    found_sciterms = []
    tweet_tokens = word_tokenize(tweet_sentence)
    for sciterm in scientific_terms:
        if sciterm in tweet_tokens:
            found_sciterms.append(sciterm)
    if len(found_sciterms) > 0:
        return True, found_sciterms
    else:
        return False, []


# Function to annotate Tweets with Cat1 heuristics
def annotate_tweets(tweets):
    """
    Annotates a DataFrame of tweets with Category 1 (Cat1) heuristic features:
    - is_claim: whether the tweet contains a claim (via `is_claim`)
    - claim_sentence: the specific sentence identified as a claim
    - has_sciterm: whether the tweet contains any scientific term
    - sciterms: list of matched scientific terms
    - is_cat1: True if both a claim and a scientific term are present

    Parameters:
        tweets (pd.DataFrame): DataFrame containing a 'text' column with tweet content.

    Returns:
        pd.DataFrame: Annotated DataFrame with additional heuristic columns.
    """
    res = tweets['text'].apply(is_claim)
    res = list(map(list, zip(*res)))
    tweets['is_claim'] = res[0]
    tweets['claim_sentence'] = res[1]

    res = tweets['text'].apply(lambda x: contains_scientific_term(x))
    res = list(map(list, zip(*res)))
    tweets['has_sciterm'] = res[0]
    tweets['sciterms'] = res[1]

    tweets["is_cat1"] = (tweets["is_claim"] & tweets["has_sciterm"])

    return tweets


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Load data from a TSV file.")
    parser.add_argument('data_path', type=str, help='Path to the input data TSV file')

    args = parser.parse_args()

    data = pd.read_csv(args.data_path, sep='\t')

    print('Run heuristics for category 1.1')
    data = annotate_tweets(data)

    data.to_csv(args.data_path.replace(".tsv", "_cat1.tsv"), sep="\t", index=False)
