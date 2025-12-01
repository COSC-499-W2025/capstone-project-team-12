# Week 13 (11/24/2025 - 11/30/2025)

## Team 12

### Team Members

| Name             | GitHub Username |
|------------------|-----------------|
| Sithara Chari    | sitharachari    |
| Madelyn DeGruchy | maddydeg        |
| Devin Huang      | devin201o       |
| Lexi Loudiadis   | lexilouds       |
| Sara Srinivasan  | Eveline36       |
| An Tran          | antran-17       |

### Work Done
- Implemented the local llm and online llm into the main pipeline (#195)
- Implemented the stats and data cache into main pipeline
- Implemented the database manager module:
  - Added saving, reading and removing databbase functions for various elements
  - Created tests for the database module (#216)
- Refactored various modules so that only the topic vectors are passed into the llm client instead of whole bundle (#232)
- Fixed an issue with the response time with the local llm.
- Updated main.py, topic_vectors.py and both llm modules (mostly prompt changes)
- Refactor metadata analyzer to return a dictionary
- Add preview of metadata analysis results to main.py
- Add metadata analysis to stats cache
- Finished the implementation of our project analysis, which uses import lines to extract skills in Git repos. Ensure milestone requirements were satisfied. Included relevant testing
- Updated the project analysis pipeline to separate the extraction data returned from the analysis data returned to allow for saving to their respective databases
- Moved extraction to the processing pipeline to ensure analysis is exclusively related to that analysis, as the file was beginning to get quite large
- Refactored the testing to move the extraction to the processing testing and added additional cases to improve coverage
- Implemented the combined preprocess module to handle the data flow of the code and text pre-processing pipelines
- Included some minor logic fixes/updates and minor bug fixes in PII removal



### Burnup chart & Task Table
<img width="921" height="482" alt="image" src="https://github.com/user-attachments/assets/7d45c92d-5594-4885-95aa-cfc82c1d154b" />
<img width="1191" height="414" alt="image" src="https://github.com/user-attachments/assets/d9e7547f-3258-465f-8681-322b053cf848" />


### In Progress
- Film demo video for milestone 1
- Working on our slide deck
### Upcoming plans
- Complete MVP for milestone 1
- Refactor different modules for a better processing time for the pipeline

### Reflections
- This week was a productive weel, we linked the different componenets we were working on into main
  - In the process, we have also discovered multiple bugs and unexpected behavior that we fixed right away
