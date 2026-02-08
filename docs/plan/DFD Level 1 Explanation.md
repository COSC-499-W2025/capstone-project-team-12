# Level 1 DFD Diagram and Explanation

![DFD Level 1](imgs/Level%201%20DFD.svg)

## LLM Consent and User Settings

Our DFD diagram begins with the user providing consent for, or refusing consent for, the use of LLMs in our analysis. Their response along with other user preferences are saved to the User Setting Datastore.

## File loading, Classification and Preprocessing

Then the system validates the file type and structure, parsing and classifying the files into code and text and GitHub repo categories. Each file is then preprocessed according to its classification.

- Text files are tokenized, stemmed and lemmatized and prepared as Bag-of-Words (BoW) for skill and topic extraction.
- User-defined identifiers are extracted from code files, then stemmed and lemmatized and added to BoW.
- GitHub repos are sent directly to Project Analysis
- Generated filetrees and filedata, referred simply as files is also saved in storage

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

## Storage

The core unit of our db is an 'Analysis' that binds together all of the Vectors,Stats, Insights , Results, Resumes and Portfolios with one unique uuid which can be used by the user to retrieve and edit any part of a previous analysis.

All tracked files, statistics, timelines topic vectors etc are treated as raw data and saved as to table 'Tracked data' in the db referred to as Data Tables

All filetrees and filedata or 'files' are saved to 'Filetrees' Table and ''Filesets' table referred to as 'File Tables'

Skills, Resumes and Portfolio is bundled as 'Results' and is saved to 'Resumes' table and 'Portfolios' table, referred to in the diagram as 'Result Tables'

All of these are stored as JSON files with the exception of filedata which is saved as binary

## Output to User

The generated analysis is converted to various graphs, points and html pages to be displayed to the user along with a resume and portfolio. The html pages can then be exported as a .docx or .pdf to the user's host system as well as the resume and portfolio.

The user can also browse past analyses in the timeline viewer or open a past analysis and add incremental changes to add/edit any of the past analyses.

### Thumbnail Assosciation

The user can also optionally provide and image path from which an image is retrieved and stored in database to represent a particular analysis.
