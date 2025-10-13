![DFD Level 1](imgs/Level%201%20DFD.png)

# DFD Level 1 Explanation

## LLM Consent and User Settings
Our DFD diagram begins with the user providing consent for, or refusing consent for, the use of LLMs in our analysis. Their response along with other user preferences are saved to the User Setting Datastore. 


## File loading, Classification and Preprocessing
Then the system validates the file type and structure, parsing and classifying the files into code and text and GitHub repo categories. Each file is then preprocessed according to its classification. 
- Text files are tokenized, stemmed and lemmatized and prepared as Bag-of-Words (BoW) for skill and topic extraction.
- User-defined identifiers are extracted from code files, then stemmed and lemmatized and added to BoW. 
- GitHub repos are sent directly to Project Analysis

## Analysis
### BoW analysis

The Bag of Words generated from text files and code identifiers is passed along to the local ML Topic Identification Model which generates a topic vector, composed of identified topics and their strengths.

### Metadata Analysis

Metadata analysis looks at file breakdown by text vs code vs images to provide a high-level overview of user activity, along with regularity of modification, etc. to identify user activity levels. For example, a coder will have lots of code but an artist might have lots of images.

### Project analysis

The project analysis is made of two halves: the package identification pipeline and the contributions pipeline.

#### Package identification

All code files in GitHub repos are scraped for import lines and requirements/dependency documentation to identify the user's proficiency in various code extensions, libraries, etc. These stats are then tallied and compiled.

#### Contributions Analysis

We will use the pydriller library to decode the timeline of actions within the .git hidden folder of all git repos. This information will be compiled to identify the user's git activity, timelines, etc. to identify skill areas, activity frequency, authorship vs management ability, etc.

## Insights Generation
These analyses will feed into the Generate Insights process, which will compile portfolio-ready summaries, rank contributions, highlight key projects, and more. 
If the user has granted consent for the use of an LLM, the report will be generated with the help of an online LLM. However, if consent is not obtained, the system will bypass the LLM and route the data through the Local Summary Generator process, which performs an offline analysis using a combination of fixed sentence templates and NL generation using ML models.

The final result will be a structured data file of one of the following formats: .txt, .csv, or JSON (yet to be finalized). That provides an overall view of all the analyses.

## Storage

All generated insights are stored in the 'Insights Database', which acts as the system's primary method for saving and retrieving analysis results. This allows users to access previously generated portfolio information, retrieve resume items, and prevent files from being duplicated in future analyses, etc. 

We also store the unanalyzed data in a 'RAW Data' Datastore that has a foreign key reference to a previously generated result which allows for incremental changes to past results.

Additionally, the User Configurations Database stores user preferences such as preferred output formats and layout preferences so that the system can later recall without the need to re-prompt the user.

## Output to User

The stored insights are then used to generate an interactive .html page along with resume-ready points. The html pages can then be exported as a .docx or .pdf to the user's host system. 

The user can also browse past analyses in the timeline viewer or open a past analysis and add incremental changes to allow for any of the past generated results.
