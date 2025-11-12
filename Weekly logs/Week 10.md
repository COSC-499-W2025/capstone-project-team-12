# Week 9 (10/27/2025 - 11/02/2025)

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
- Wrote pytests for file_manager.py and edited file_manager.py to reflect new changes that came out during testing process
- Researched how to use pyLDAvis for our exact purposes
- Resolved bug that was preventing system from properly reconstructing .git folders
  - Made changes to tree_processor.py to prevent files in .git folder from being dropped as invalid nodes
- Slight refactor of repository_processor.py to return List[Dict[str, Any]] instead of the JSON formatted version for consistency with other pipelines. Previous implementation was due to misunderstanding so reverted to the more basic version.
- Implemented testing to ensure .git files are not dropped in error in the future
- Implemented testing to check the return from the Repository Processor
- Implemented the BoW Cache, which stores and retrieves tokenized text before text analysis, given a hash key
- Implemented unit tests for the BoW Cache
- Investigated problems with path and environment configurations that was causing tests to fail and unexpected output
- Implemented a basic version of the statistics and data cache (#136)
- Wrote testing for the statistics and data cache (#136)
- Wrote testing for the error handling for tree_processor.py (#122)
- Implement metadata extractor and metadata analyzer
  
### Burnup chart & Task Table

[//]: # "ADD IMAGES after all the work is pushed"

![Week 10 Burn Up](/imgs/Week%2010%20Burnup.png)

![Week 10 Tasks Table](/imgs/Week%2010%20Team%20Tasks.png)
Filtered to only show Tasks with changes this week.

### In Progress
- Further metadata analysis from extraction
- Further project analysis from extraction
- Implementing the ML model to create topic vectors
- Began implementation of extraction of key statistics from .git folder. Notes on PR indicate that this is not the final version, since I want to ensure we are covering all necessary statistics to meet Milestone 1 Requirements. Current implementation is very strong start and covers the majority of what needs to be considered.

### Upcoming plans
- 

### Reflections
- Some delays in logs so this one is coming later, individual logs were completed on time.
- Last week was a very busy one for all team members, so are planning to make the most of this reading week to ensure we are still on track for the end of the month.
