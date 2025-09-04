# SciTweets Detection Heuristics

## Description

This method offers a computationally inexpensive and fully transparent way to identify scientific online discourse from a dataset of social media posts. It was originally developed for analyzing tweets, but can be used for all types of social media posts. It applies word-based heuristics (see [Technical Details](#technical-details)) to identify three different forms of scientific relevance in posts:

- Category 1: The post contains a claim or question that can be scientifically verified
- Category 2: The post references scientific findings
- Category 3: The post mentions a scientific research context

The strength of the method lies in its transparency, as it is based exclusively on rules that are understandable to humans.

## Use Cases

- To quickly and transparently create a social media dataset in which scientific online discourse occurs significantly more frequently than in the original data.  To do this, the method is applied to a very large dataset of social media posts and all posts that do not fall into any of the three categories according to the method are filtered out. Example:

  Hafid, S., Schellhammer, S., Bringay, S., Todorov, K., & Dietze, S. (2022, October). SciTweets-a dataset and annotation framework for detecting scientific online discourse. In *Proceedings of the 31st ACM International Conference on Information & Knowledge Management* (pp. 3988-3992).

## Input Data

The method accepts a [tab-separated value file](https://en.wikipedia.org/wiki/Tab-separated_values) with at least one `text` column as input. The category 2 heuristics also require a 'urls' column with all resolved URLs of the main text (i.e., the actual target URLs, not the shortened ones like “https://t.co/xxx”) as a comma-separated list of strings (possibly empty) in square brackets. The input file can contain any other columns (e.g., with the post IDs). All columns in the input file are copied to the output file, with new columns added to the right.

Example input data ([data/example_tweets.tsv](data/example_tweets.tsv)):

| text | urls |
|------|------|
| In @sciencemagazine: Rare variant found that raises HDL cholesterol and increases risk of coronary heart disease: https://t.co/4xpL3KlGy9 | ['https://www.science.org/doi/full/10.1126/science.aad3517'] |
| Teach children to treat animals responsibly do not teach captivity! Join us http://t.co/UR15gQPatU #FreeAllCetacea via @FreeAllCetacea | ['http://www.wdcs.org/'] |
| Violence is a leading cause of death for Americans 10-24 yrs old. @NICHD_NIH research on youth violence prevention https://t.co/9ZD58zGUhI | ['https://1.usa.gov/1q0MqOd/'] |
| "“At a point now where I understand plant temperaments — how vulnerable they are, but also how strong they can become"" #Precision #AgTech" | [] |

## Output Data

This method adds the output of the heuristics as new columns to the right of the input data. The new columns `is_catX` (`X` being 1, 2 or 3), contains `True` in a row if the respective text is identified to be from a scientific discourse as per category `X`. For full transparency, the other new columns provide the output of all intermediate steps of the heuristics (see [Technical Details](#technical-details)).

The heuristics are applied one category at a time. If the heuristics are applied in sequence to the example data (See [How to Use](#how-to-use)), the output is the same as in ([data/example_tweets_cat1_cat2_cat3.tsv](data/example_tweets_cat1_cat2_cat3.tsv)):

| text | is_claim | claim_sentence | has_sciterm | sciterms | is_cat1 | urls | sci_subdomain | has_sci_subdomain | sci_mag_domain | has_sci_mag_domain | sci_news_domain | has_sci_news_domain | is_cat2 | mentions_science_research_in_general | mentions_scientist | mentions_publications | mentions_research_method | is_cat3 |
|------|----------|----------------|-------------|----------|---------|------|---------------|-------------------|----------------|--------------------|-----------------|---------------------|---------|--------------------------------------|--------------------|-----------------------|--------------------------|---------|
| In @sciencemagazine: Rare variant found that raises HDL cholesterol and increases risk of coronary heart disease: https://t.co/4xpL3KlGy9 | True | in @sciencemagazine: rare variant found that raises hdl cholesterol and increases risk of coronary heart disease: https://t.co/4xpl3klgy9 | True | ['cholesterol', 'disease', 'heart', 'risk', 'variant'] | True | ['https://www.science.org/doi/full/10.1126/science.aad3517'] | www.science.org | True | www.science.org | True |  | False | True |  |  |  |  | False |
| Teach children to treat animals responsibly do not teach captivity! Join us http://t.co/UR15gQPatU #FreeAllCetacea via @FreeAllCetacea | True | teach children to treat animals responsibly do not teach captivity! | True | ['animals'] | True | ['http://www.wdcs.org/'] |  | False |  | False |  | False | False |  |  |  |  | False |
| Violence is a leading cause of death for Americans 10-24 yrs old. @NICHD_NIH research on youth violence prevention https://t.co/9ZD58zGUhI | True | violence is a leading cause of death for americans 10-24 yrs old. | True | ['prevention', 'research'] | True | ['https://1.usa.gov/1q0MqOd/'] |  | False |  | False |  | False | False | research on |  |  |  | True |
| "“At a point now where I understand plant temperaments — how vulnerable they are, but also how strong they can become"" #Precision #AgTech" | False |  | True | ['plant'] | False | [] | [] | False | [] | False | [] | False | False |  |  |  |  | False |

## Hardware Requirements

This method has low hardware requirements. For example, it runs on a small machine with 1 x86 CPU core, 2 GB RAM, and 2 GB HDD. This method can run out of memory if your dataset is too large to fit into main memory (RAM).

## Environment Setup

This method requires at least Python version 3.9. To avoid problems with your system's Python installation, create and activate a [virtual environment](https://docs.python.org/3/library/venv.html).

Then install all requirements using:

```{bash}
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

## How to Use

Apply the heuristics for each category to the [example input data](data/example_tweets.tsv), then display the result:

```{bash}
# Apply category 1 heuristics and write to data/example_tweets_cat1.tsv
python3 src/apply_cat1_claim_question_heuristics.py data/example_tweets.tsv

# Apply category 2 heuristics and write to data/example_tweets_cat1_cat2.tsv
python3 src/apply_cat2_reference_heuristics.py data/example_tweets_cat1.tsv

# Apply category 3 heuristics and write to data/example_tweets_cat1_cat2_cat3.tsv
python3 src/apply_cat3_research_context_heuristics.py data/example_tweets_cat1_cat2.tsv

# Display result
cat data/example_tweets_cat1_cat2_cat3.tsv
```

## Technical Details

This method employs a set of simple human-made rules ("heuristics") to identify whether a social media post falls into one of three categories related to scientific online discourse. The heuristics for each category are explained below:

- Category 1 Heuristic: The post contains a claim or question that can be scientifically verified *if*
    - it contains a verb that from a [list of verbs](src/lists/predicates.txt) that we extracted from four research works on claims [1-4], and which is neither preceded nor followed by a personal pronoun, possessive pronoun noun or adjective in the same sentence, but is preceded by a noun and followed by a noun or by an adjective.

- Category 2: The post references scientific findings
- Category 3: The post mentions a scientific research context

    **Heuristics for Category 1.1:** To find tweets for category 1.1, the final heuristic comprises two heuristics combined with a logical AND operator:
    - Heuristic 1: pattern-matching for subject-predicate-object patterns (more specifically: noun-verb-noun and noun-verb-adjective patterns) where the predicate must come from a list of predefined predicates (e.g, « cause », « lead to », « help with ») that we extracted from different research works on claims [1-4].
    - Heuristic 2: scientific term filter where we only keep tweets that contain at least one term from a predefined list of ~30k scientific terms that come from Wikipedia Glossaries, from which we hand-picked the categories that we deemed to be related to science (e.g, « medicine », « history », « biology »).

- **Category 1.2 - Reference to scientific knowledge:** Does the text include at least one reference to scientific knowledge? References can either be direct, e.g., DOI, title of a paper, or indirect, e.g., a link to an article that includes a direct reference

    **Heuristics for Category 1.2:** To find tweets for category 1.2, the heuristic checks whether a tweet contains a URL with a subdomain that is included in a
predefined list of 17,500 scientific domains and subdomains from open access repositories, newspaper science sections, and science magazines (e.g., “link.springer.com“, “sciencedaily.com“).

    Number of scientific domains and subdomains per type:

    | Type                       | Number of domains and subdomains |
    |----------------------------|:--------------------------------:|
    | Open Access Repositories   |              17,463              |
    | Newspaper Science Sections |                23                |
    | Science Magazines          |                14                |
    | Total                      |              17,500              |

    *Open Access Repositories*

    The list of 17,463 subdomains is collected as follows:
    - All full-text links included in the public CrossRef Snapshot from January 2021 ([Link](https://academictorrents.com/details/e4287cb7619999709f6e9db5c359dda17e93d515)) were extracted
    - Using the CrossRef API, we extracted the full-text links that were registered after January 2021
    - All extracted links were annotated with their subdomain using the Python library [tldextract](https://github.com/john-kurkowski/tldextract)
    - The frequency for every subdomain was computed  
    - We excluded subdomains with a frequency lower than 50
    - We excluded 38 subdomains that are not scientific (e.g., "youtube.com", "yahoo.com")
    - We added 46 subdomains from a manually curated list (e.g., "semanticscholar.org", "www.biorxiv.org")

    To filter tweets that refer to Open Access Repositories, the tweets must contain a URL with a subdomain from this list. 

    *Newspaper Science Sections*

    The list of 23 Newspaper Science Sections is manually curated and contains domains from major newspaper outlets in the English language that have a dedicated science section.
    To filter tweets that refer to Newspaper Science Sections, the tweets must contain a URL with a subdomain from this list **AND** include "/science".

    *Science Magazines*

    The list of 14 Science Magazines domains and subdomains is manually curated.
    To filter tweets that refer to Science Magazines, the tweets must contain a URL with a subdomain from this list.


- **Category 1.3 - Related to scientific research in general:** Does the text mention a scientific research context (e.g., mention of a scientist, scientific research efforts, research findings)?

  **Heuristics for Category 1.3:** To find tweets for category 1.3, four different heuristics are combined with a logical OR operator:
  - Heuristic 1: includes tweets that mention scientists, i.e., that have a noun from a predefined list, e.g., "research team", "research group", "scientist", "researcher", "psychologist", "biologist", "economist"
  - Heuristic 2: includes tweets that mention research, i.e., that have a noun from a predefined list, e.g., 'research on', 'research in', 'research for', 'research from', 'science of', 'science to', 'science', 'sciences of'
  - Heuristic 3: tweets that mention a research method, i.e., that have a word from a predefined list of social science methods, collected from SAGE Social Science Thesaurus (see sc_methods.txt) [Link](https://concepts.sagepub.com/vocabularies/social-science/en/page/?uri=https%3A%2F%2Fconcepts.sagepub.com%2Fsocial-science%2Fconcept%2Fconceptgroup%2Fmethods)
  - Heuristic 4: includes tweets that mention research outcomes, i.e., that have a noun from a predefined list, e.g.,'publications', 'posters', 'reports', 'statistics', 'datasets', 'findings'

## References

[1] Pinto, J. M. G., Wawrzinek, J., & Balke, W. T. (2019, June). What Drives Research Efforts? Find Scientific Claims that Count!. In 2019 ACM/IEEE Joint Conference on Digital Libraries (JCDL) (pp. 217-226). IEEE.

[2] González Pinto, J. M., & Balke, W. T. (2018, September). Scientific claims characterization for claim-based analysis in digital libraries. In International Conference on Theory and Practice of Digital Libraries (pp. 257-269). Springer, Cham.

[3] Kilicoglu, H., Rosemblat, G., Fiszman, M., & Rindflesch, T. C. (2011). Constructing a semantic predication gold standard from the biomedical literature. BMC bioinformatics, 12(1), 1-17.

[4] Smeros, P., Castillo, C., & Aberer, K. (2021, October). SciClops: Detecting and Contextualizing Scientific Claims for Assisting Manual Fact-Checking. In Proceedings of the 30th ACM International Conference on Information & Knowledge Management (pp. 1692-1702).

## Contact Details

For questions or feedback, contact <sebastian.schellhammer@gesis.org>
