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
- Refactored file_classifier.py and text_preprocessor.py by adding variable and function input and output typings
- Added error handling to file_classifier.py and text_preprocessor.py
- Refactored file_classifier.py to use sets instead of lists, and altered inputs of isCode and isText
  - Updated file_classifier tests to match the new changes
- refactored tree_processor.py so that the getter functions return the nodes themselves instead of the file paths in the arrays
- Added error handling for 'main.py' and 'tree_processor,py'
- Implemented safe key access, try-except blocks for processing and classification, and node traversal resilience
- Added handling of KeyboardInterrupt and unexpected exceptions for clean exits
- PII Remover Research and Implementation
  - Added relevant testing for PII Removal
- Implemented Repository Processor and researched further .git folder extraction libraries
  - Added all relevant testing
- Swapped Spacy based pipeline to gensim due to upstream errors
- Rework text pre process to use chaining instead of nested function calls
  - Implement comprehensive pytest testing for text preprocess
- Refactor of file manager to store binary data in a separate array instead of in the nodes itself for lighter data
  - Added a function to be able to retrieve binary array without calling file manager again

### Burnup chart & Task Table

[//]: # "ADD IMAGES after all the work is pushed"

![Week 9 Burn Up](../imgs/Week%209%20Burnup.png)

![Week 9 Tasks Table](../imgs/Week%209%20Tasks.png)
Filtered to only show Tasks with changes this week.

### In Progress

- Investigating bug related to how file structure is created in order for PyDriller to be able to extract details from rebuilt file structure
  - Once this bug is resolved, the remainder of the .git extraction code will be committed.

### Upcoming plans
- Begin text analysis and meta data analysis implementation
- Assign further tasks for coming weeks to ensure MVP for end of November
- Start ML implementation

### Reflections
- Encountered a bug while developing PyDriller that has caused some issues in that implementation. May continue to slow down that specific pipeline but am working towards the bug fix
- Adding comprehensive type hints across moduleshas assisted in catching bugs early and making the codebase much easier to navigate for the entire team.
- We are wanting to ensure that we are taking large enough steps through the week to ensure that we will be able to have the MVP by November 30 and will continue to have team discussions on how to prioritize work in the coming weeks
