import argparse
import en_core_web_sm
import re
import pandas as pd
from nltk.tokenize import sent_tokenize, word_tokenize
nlp = en_core_web_sm.load()

# Load predicates
with open('predicates.txt', 'r') as f:
    predicates = [line.strip() for line in f]

# Load scientific terms
def load_scientific_terms():
    with open('wiki_sci_terms.txt', 'r') as f:
        wiki_sci_terms = [line.strip() for line in f]

    with open('sc_methods.txt', 'r') as f:
        sc_methods_terms = [line.strip() for line in f]

    scientific_terms = wiki_sci_terms + sc_methods_terms
    scientific_terms.sort()

    for i in range(len(scientific_terms)):
        scientific_terms[i] = scientific_terms[i].lower()

    # Text speak words like "lol" are collected then filtered out of the scientific terms list
    text_speak_wordlist = ['lol','lmao','lmfao', 'omg', 'ppl', 'pls','thx','sry','dah', 'dat', 'soo', 'isn', 'stan','abt', 'dawg','cha','jk']
    # 500 false scientific words are collected then taken away from the scientific terms list, by a process of using the sciterm heuristic and looking at the
    # most frequent words collected
    false_scientific_words_list = ['haven', 'practice','fans','call','place','special','account','young','small','point','games','act','join','past','words','events','respect','simple','current','student','major','account','cover','moment', 'direct','complete','five','cute','club','non','final','voice','essential','date','tour','ads','till','card','youtube','write','pitch','interviews','duo','cant','even','community', 'force', 'support', 'even', 'food', 'associated', 'death', 'say', 'author', 'find', 'reading', 'being', 'work', 'air', 'storms', 'security', 'real', 'say', 'kissing', 'day', 'need', 'support', 'feedback', 'being', 'perfect', 'religious', 'curriculum', 'good', 'line', 'schools', 'women', 'link', 'meet', 'mind', 'eyes', 'crew', 'support', 'being', 'work', 'ago', 'load', 'associated', 'clean', 'first', 'insurance', 'year', 'end', 'good', 'lie', 'support', 'nah', 'rain', 'good', 'share', 'time', 'support', 'support', 'bird', 'bus', 'grade', 'groups', 'good', 'linked', 'negative', 'self', 'number', 'real', 'support', 'satellites', 'tap', 'wire', 'world', 'support', 'problem', 'range', 'resource', 'support', 'day', 'support', 'trade', 'almost', 'authority', 'symptoms', 'women', 'strength', 'support', 'centre', 'footprint', 'sets', 'groups', 'higher', 'resolution', 'series', 'volatile', 'fly', 'support', 'minor', 'first', 'time', 'tax', 'game', 'associated', 'good', 'year', 'markets', 'symptoms', 'driver', 'lesson', 'support', 'women', 'support', 'support', 'world', 'sink', 'time', 'change', 'cost', 'green', 'scope', 'speed', 'key', 'angles', 'end', 'scheme', 'free', 'support', 'message', 'carrier', 'communications', 'support', 'package', 'cactus', 'fruit', 'being', 'full', 'support', 'strong', 'action', 'good', 'free', 'hotspot', 'internet', 'support', 'local', 'support', 'entertainment', 'bit', 'groups', 'support', 'need', 'value', 'emotions', 'negative', 'night', 'support', 'complex', 'freezing', 'province', 'rain', 'snow', 'killing', 'plan', 'global', 'kind', 'movement', 'message', 'support', 'schools', 'peace', 'prayer', 'pressure', 'cars', 'support', 'demand', 'food', 'free', 'effectiveness', 'food', 'medications', 'design', 'ear', 'vibration', 'debt', 'service', 'head', 'school', 'line', 'local', 'internal', 'support', 'reason', 'web', 'negative', 'find', 'higher', 'zoning', 'collection', 'compliance', 'catastrophic', 'control', 'stand', 'support', 'learning', 'mental', 'students', 'support', 'entity', 'laws', 'even', 'process', 'year', 'family', 'spread', 'support', 'understanding', 'want', 'positive', 'good', 'note', 'time', 'top', 'being', 'activity', 'higher', 'active', 'burn', 'change', 'color', 'red', 'aging', 'being', 'fix', 'processes', 'eventually', 'label', 'energy', 'need', 'support', 'time', 'change', 'journey', 'related', 'support', 'fire', 'stream', 'being', 'expression', 'free', 'speaking', 'group', 'member', 'support', 'class', 'classes', 'community', 'game', 'grade', 'play', 'school', 'second', 'skills', 'students', 'time', 'matter', 'world', 'child', 'greedy', 'sound', 'support', 'interaction', 'leadership', 'member', 'position', 'blocking', 'need', 'reason', 'support', 'case', 'list', 'community', 'depreciation', 'assembly', 'support', 'total', 'behaviors', 'change', 'negative', 'positive', 'higher', 'world', 'year', 'industry', 'support', 'activists', 'century', 'food', 'critical', 'mental', 'positive', 'thinking', 'thought', 'energy', 'support', 'country', 'site', 'group', 'front', 'support', 'energy', 'higher', 'independence', 'prices', 'industry', 'year', 'sign', 'face', 'problem', 'support', 'world', 'want', 'information', 'matrix', 'power', 'prayer', 'reason', 'say', 'world', 'back', 'city', 'energy', 'habit', 'support', 'hair', 'event', 'first', 'link', 'second', 'support', 'child', 'governor', 'support', 'age', 'children', 'game', 'groups', 'reverse', 'training', 'touch', 'back', 'culture', 'good', 'need', 'real', 'time', 'annual', 'spring', 'real', 'women', 'need', 'relief', 'support', 'gesture', 'support', 'enough', 'harvesting', 'interference', 'enough', 'household', 'need', 'range', 'discussion', 'information', 'patent', 'support', 'data', 'group', 'groups', 'lots', 'span', 'year', 'being', 'list', 'top', 'landslide', 'support', 'bit', 'killing', 'channel', 'end', 'ran', 'standards', 'revolution', 'absolutely', 'entire', 'need', 'thread', 'digital', 'support', 'back', 'situation', 'breaking', 'industry', 'path', 'support', 'music', 'participation', 'similar', 'face', 'support', 'role', 'product', 'big', 'primary', 'significant', 'support', 'mad', 'being', 'path', 'link', 'group', 'handle', 'need', 'school', 'students', 'support', 'teachers', 'country', 'day', 'source', 'vital', 'class', 'want', 'wealth', 'work', 'end', 'host', 'focus', 'root', 'support', 'time', 'world', 'students', 'support', 'add', 'bar', 'bit', 'couple', 'film', 'set', 'star', 'support', 'motor', 'city', 'support', 'cut', 'finds', 'play']
    scientific_terms = [term for term in scientific_terms if (term not in text_speak_wordlist) and (term not in false_scientific_words_list) ]
    return scientific_terms

scientific_terms = load_scientific_terms()


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
    parser = argparse.ArgumentParser(description="Load tweet data from a TSV file.")
    parser.add_argument('tweet_data_path', type=str, help='Path to the input tweet data TSV file')

    args = parser.parse_args()

    tweet_data = pd.read_csv(args.tweet_data_path, sep='\t')

    print('Run heuristics for category 1.1')
    tweet_data = annotate_tweets(tweet_data)

    tweet_data.to_csv(args.tweet_data_path.replace(".tsv", "_cat1_heuristics.tsv"), sep="\t", index=False)