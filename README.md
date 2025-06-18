# SciTweets Heuristics - Heuristics of Science-Relatedness of Tweets

## Description
This repository contains three scripts to classify the science-relatedness of Tweets with heuristics. The heuristics were developed as part of *"SciTweets - A Dataset and Annotation Framework for Detecting Scientific Online Discourse"* published at **CIKM2022**. The scripts include heuristics for the following three different forms of science-relatedness for Tweets (categories 1.1, 1.2, and 1.3):



![Image Alt Text](categories_science_relatedness.png)

**Category 1 - Science-related**: Texts that fall under at least one of
the following categories:

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;**Category 1.1 - Scientific knowledge (scientifically verifiable claims)**: Does the text include a claim or a question that
could be scientifically verified? 

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;**Category 1.2 - Reference to scientific knowledge**: Does
the text include at least one reference to scientific knowledge?
References can either be direct, e.g., DOI, title of a paper or
indirect, e.g., a link to an article that includes a direct reference

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;**Category 1.3 - Related to scientific research in general**:
Does the text mention a scientific research context (e.g., mention
of a scientist, scientific research efforts, research findings)? 

**Category 2 - Not science-related**: Texts that don’t fall under
either of the 3 previous categories. 

## Heuristics

### Heuristics for Category 1.1 
To find tweets for category 1.1, the final heuristic comprises two heuristics combined with a logical AND-operator :
1. Heuristic 1: pattern-matching for subject-predicate-object patterns (more specifically: noun-verb-noun and noun-verb-adjective patterns) where the predicate must come from a list of predefined predicates (e.g « cause », « lead to », « help with ») that we extracted from different research works on claims [1-4].
2. Heuristic 2: scientific term filter where we only keep tweets that contain at least one term from a predefined list of ~30k scientific terms that come from Wikipedia Glossaries from which we hand-picked the categories that we deemed to be related to science (e.g « medicine », « history », « biology »). 

### Heuristics for Category 1.2
To find tweets for category 1.2 the heuristic checks whether a tweet contains a URL with a subdomain that is included in a
predefined list of 17,500 scientific domains and subdomains from open access repositories, newspaper science sections and science magazines (e.g., “link.springer.com“, “sciencedaily.com“).

Number of scientific domains and subdomains per type:

| Type                       | Number of domains and subdomains |
|----------------------------|:--------------------------------:|
| Open Access Repositories   |              17,463              |
| Newspaper Science Sections |                23                |
| Science Magazines          |                14                |
| Total                      |              17,500              |

#### Open Access Repositories 
The list of 17,463 subdomains is collected as follows:
1. all full-text links included in the public CrossRef Snapshot from January 2021 ([Link](https://academictorrents.com/details/e4287cb7619999709f6e9db5c359dda17e93d515)) were extracted
2. using the CrossRef API we extracted the full-text links that were registered after January 2021
3. all extracted links were annotated with their subdomain using the python library [tldextract](https://github.com/john-kurkowski/tldextract)
4. the frequency for every subdomain was computed  
5. we excluded subdomains with a frequency lower than 50
6. we excluded 38 subdomains that are clearly not scientific (e.g., "youtube.com", "yahoo.com")
7. we added 46 subdomains from a manually curated list (e.g., "semanticscholar.org", "www.biorxiv.org")

To filter tweets that refer to Open Access Repositories, the tweets must contain a URL with a subdomain from this list. 

#### Newspaper Science Sections
The list of 23 Newspaper Science Sections is manually curated and contains domains from major newspaper outlets in english language, that have a dedicated science section.
To filter tweets that refer to Newspaper Science Sections, the tweets must contain a URL with a subdomain from this list **AND** includes "/science".

#### Science Magazines
The list of 14 Science Magazines domains and subdomains is manually curated.
To filter tweets that refer to Science Magazines, the tweets must contain a URL with a subdomain from this list.

### Heuristics for Category 1.3
To find tweets for category 1.3, four different heuristics are combined with a logical OR-operator:
1. Heuristic 1: includes tweets that mention scientists, i.e., that have a noun from a predefined list, e.g., "research team", "research group", "scientist", "researcher", "psychologist", "biologist", "economist"
2. Heuristic 2: includes tweets that mention research, i.e., that have a noun from a predefined list, e.g., 'research on', 'research in', 'research for', 'research from', 'science of', 'science to', 'science', 'sciences of'
3. Heuristic 3: tweets that mention a research method, i.e., that have a word from a predefined list of social science methods, collected from SAGE Social Science Thesaurus (see sc_methods.txt) [Link](https://concepts.sagepub.com/vocabularies/social-science/en/page/?uri=https%3A%2F%2Fconcepts.sagepub.com%2Fsocial-science%2Fconcept%2Fconceptgroup%2Fmethods)
4. Heuristic 4: includes tweets that mention research outcomes, i.e., that have a noun from a predefined list, e.g.,'publications', 'posters', 'reports', 'statistics', 'datasets', 'findings'

## Keywords
Science-Relatedness, Scientific Online Discourse, Tweets, Claims, Heuristics


## Usecase
The heuristics can be used to extract scientific online discourse from Twitter data (Tweets that are science-related). The extracted Tweets could be (1) analyzed or (2) used as input for subsequent methods like claim verification or reference disambiguation.


## Repo Structure
This repository contains the following directories and files:

1. **heuristics** the python script for classifying the science-relatedness of Tweets
   1. **cat1_sciknowledge.py** code to run heuristics for category 1.1
   2. **cat2_sciurl.py** code to run heuristics for category 1.2
   3. **cat3_research.py** code to run heuristics for category 1.3
   4. **news_outlets_domains.csv** domains and subdomains from major news outlets
   6. **repo_subdomains.csv** domains and subdomains from open access repositories 
   7. **sc_methods.txt** list of scientific methods from SAGE Social Science Thesaurus [Link](https://concepts.sagepub.com/vocabularies/social-science/en/page/?uri=https%3A%2F%2Fconcepts.sagepub.com%2Fsocial-science%2Fconcept%2Fconceptgroup%2Fmethods)
   8. **science_mags_domains.csv** domains and subdomains from science magazines
   9. **wiki_sci_terms.txt** list of scientific terms extracted from wikipedia glossaries
2. **example_tweets.tsv** an examplary input dataset in tsv format (tab separated) 
3. **example_tweets_cat1_heuristics.tsv** an examplary output dataset in tsv format (tab separated) after running cat1_sciknowledge.py
4. **example_tweets_cat2_heuristics.tsv** an examplary output dataset in tsv format (tab separated) after running cat2_sciurl.py
5. **example_tweets_cat3_heuristics.tsv** an examplary output dataset in tsv format (tab separated) after running cat3_research.py

## Setup


### Environment Setup
To run the heuristics the following software is required. 

First, the script requires a Python environment with a version >= 3.9
1. Python >= 3.9

Second, within the Python environment, install the modules from **requirements.txt** with

    python -m pip install -r requirements.txt

Note, the script might also run properly with different versions of the modules. 

Third, the spacy module requires the model "" to be downloaded before running the heuristics scripts with:
    
    python -m spacy download en_core_web_sm

### Hardware Requirements (Optional)
Running the heuristics scripts does not require specific hardware.

# Input Data
The input data has to be a .tsv file (tab separated) containing the input Tweets. The input file needs to have a _text_ column for the heuristics for categories 1.1 and 1.3, and a _urls_ column for the category 1.2 heuristics script.
All other columns in the input file will not be used by the scripts and will stay the same in the output file.


## Sample Input and Output Data
The file **example_tweets.tsv** contains exemplary input data. After running any of the heuristics (**cat1_sciknowledge.py**, **cat2_sciurl.py**, **cat3_research.py**) a new file will be created that contains the input data, information from the heuristics, and a column for the heuristics-derived category of science-relatedness.  

Structure of the input file:

| tweetid                    |  text  | urls |
|----------------------------|:------:|------|
| ...                        |  ...   | ...  |
| ...                        |  ...   | ...  |
| ...                        |  ...   | ...  |


Example for **cat2_sciurl.py**:

Structure of the output file after running **cat2_sciurl.py**:

| tweetid                    |  text  | urls | sci_subdomain | has_sci_subdomain | sci_mag_domain | has_sci_mag_domain | sci_news_domain | has_sci_news_domain | is_cat2 |
|----------------------------|:------:|------|---------------|-------------------|----------------|--------------------|-----------------|---------------------|---------|
| ...                        |  ...   | ...  | ...           | ...               | ...            | ...                | ...             | ...                 | ...     |
| ...                        |  ...   | ...  | ...           | ...               | ...            | ...                | ...             | ...                 | ...     |
| ...                        |  ...   | ...  | ...           | ...               | ...            | ...                | ...             | ...                 | ...     |


# How to Use
1. Install required software and modules
2. Run the scripts with (here script for category 1.1):
   
         python3 cat1_sciknowledge.py _input_file_path_
    

where the _input_file_path_ is the path on your computer/server where the input file is located.
3. After the script is finished it will save the output file to the same location as the _input_file_path_ with "_cat1_heuristics" / "_cat2_heuristics" / "_cat3_heuristics" appended to the input file filename depending on which script was run.

# Contact Details
For questions or feedback, contact sebastian.schellhammer@gesis.org

# Publication
Please cite the following paper if you are using the classifier:

*Hafid, Salim, et al. "SciTweets-A Dataset and Annotation Framework for Detecting Scientific Online Discourse." Proceedings of the 31st ACM International Conference on Information & Knowledge Management. 2022, [download](https://arxiv.org/abs/2206.07360).*

```bib
@inproceedings{hafid2022scitweets,
  title={SciTweets-A Dataset and Annotation Framework for Detecting Scientific Online Discourse},
  author={Hafid, Salim and Schellhammer, Sebastian and Bringay, Sandra and Todorov, Konstantin and Dietze, Stefan},
  booktitle={Proceedings of the 31st ACM International Conference on Information \& Knowledge Management},
  pages={3988--3992},
  year={2022}
}
```


## Other references
- [1] Pinto, J. M. G., Wawrzinek, J., & Balke, W. T. (2019, June). What Drives Research Efforts? Find Scientific Claims that Count!. In 2019 ACM/IEEE Joint Conference on Digital Libraries (JCDL) (pp. 217-226). IEEE.
- [2] González Pinto, J. M., & Balke, W. T. (2018, September). Scientific claims characterization for claim-based analysis in digital libraries. In International Conference on Theory and Practice of Digital Libraries (pp. 257-269). Springer, Cham.
- [3] Kilicoglu, H., Rosemblat, G., Fiszman, M., & Rindflesch, T. C. (2011). Constructing a semantic predication gold standard from the biomedical literature. BMC bioinformatics, 12(1), 1-17.
- [4] Smeros, P., Castillo, C., & Aberer, K. (2021, October). SciClops: Detecting and Contextualizing Scientific Claims for Assisting Manual Fact-Checking. In Proceedings of the 30th ACM International Conference on Information & Knowledge Management (pp. 1692-1702).
