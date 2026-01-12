# Week 8 (10/20/2025 - 10/26/2025)

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

- Refactor of File Classifier and Tree Processor to consider nodes from the file manager node attribute structure and to drop unhandled nodes
- Added clearly defined output functions to the tree processor to allow for processed files to be handled easily in downstream processes
- File Manager refactor to update how attributes are attached to the nodes
- Addition of test directories for file manager testing
- Created implementation and tests for code pre-processing pipeline
- Creation of main.py to serve as the user entry point and to run tests currently
- Debugged and Added Persistence to Dockerized postgres db

### Burnup chart & Task Table

[//]: # "ADD IMAGES after all the work is pushed"

![Week 8 Burn Up](../imgs/Week%208%20Burnup.png)

![Week 8 Tasks Table](../imgs/Week%208%20Tasks.png)
Filtered to only show Tasks with changes this week.

### In Progress

- Investigating bug with spacy and relevant refactoring required
- Likely rewrite of code_proprocessor

### Upcoming plans

- Rework all modules to conform to stricter coding standards
- Meet to discuss how we want to assign upcoming tasks
- Team check-in to ensure we are on track for Milestone 1 presentations at the end of next month
- Organize future issues to be assigned as best as can be planned for
