![System Architecture Diagram](imgs/System%20Architecture%20Diagram.png)

# Software Architecture Explanation

## File Handling

- The CLI interfaces directly with the backend for all of it's functions. The Browser based GUI only interfaces with the REST API. The API is responsible for interfacing with the backend appropriately. However the files are retrieved the Architecture is the same from file manager onwards.

- The Filemanager loads the file into the memory generates a rudimentry filetree and uses the Filetree Manager to deduplicate the files.

- The Filetree Manager also generates a Fileset, files + filetree information.
  - In the case of a new analysis the fileset is simply saved to the database
  - In the case of a incremental analysis update, the new fileset is compared to the old fileset for identifying changes
  - Every filetree generated is stored to the database along with chronological information
  - Only the latest/most up-to-date fileset is kept in the database.

The finalized filesets are stored to the database along with the old and newly generated tree. This Fileset data comprised of files and filetrees is used for the next step, artifact analysis.

## Artifact Analysis

Artifact Analysis is split into 3 Distinct pipelines.

1. The **Topic Analysis** pipeline used to identify what the user's work is about by leveraging ML based analysis. The topic analysis is handled in two halves: 
    - **Code pre-process** pipeline, which extracts identifiers using Pygments and breaks the code into tokens, these tokens are forwarded to the Text Preprocess half.
    - **Text Preprocess** pipeline, which standardizes text for analysis by splitting it into tokens, dropping filler words, lemmatizing them and removing any personally identifiable information.

    The cleaned text is then stored in a Bag-of-Words (BoW) model with a built-in cache to avoid reprocessing. The BoW is then fed into the Text Analysis component, where a topic identification model produces topic vectors and statistics. The BoW Cache is saved to the database.

2. The **Project Analysis** pipeline examines the repository itself. It reads data from the project's Git history and scans import statements and package files to measure contributions and use of dependencies.

3. The **Metadata Analysis** pipeline that looks over the metadata to at high level to determine user's language proficiencies, probable role etc.

- All of the results of the 3 pipelines are bundled into a cache in-memory and is referred to as 'Extracted Data'

- The Extracted Data is then shown to the user for finetuning, the user may reorder the importance of repos, edit topic vectors etc. The edited data is referred to as 'Finalized Data.' The Finalized data is saved to the database.

- The Finalized Fata is then used to generate Natural Language Insights, A resume and A portfolio. All of these are referred to broadly as Insights and are bundled and saved to the database.

- All interactions with the database are mediated by a database manager to

Finally, the Dashboard Generator compiles these into an interactive HTML page output. Finally, the user can also export the dashboard as a static .docx or .pdf file.
