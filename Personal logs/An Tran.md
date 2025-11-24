# An Tran Personal Log (79499364)

## Week 11 (11/17/2025 - 11/23/2025)
### Tasks
- Implement metadata metadata analyzer
- Finish implementing author extraction in metadata extractor

### Completed:
- Added author extraction for pdf and docx files in metadata extractor
- Changed metadata extractor to return a dictionary with filepath as key instead of filename to prevent overwriting data
- Updated tests for metadata extractor
- Implemented metadata analyzer to return custom class of  and its tests
- Participated in team meeting

### Reflection and plans for next week
- Initially I wanted to use the metadata stats and make analyses about a user's productivity based on their files' creation/modified dates. Sara suggested I could classify the extensions into skill categories and gather the user's productivity/primary skills based on the change in each category's total file size in between modified date durations, but I couldn't figure out a way to code that for this week. Perhaps for Milestone 2, metadata analyzer could compare the change in file size by the time between each generated insight.
- To integrate metadata analysis results into main.py and store in stats cache
- Start preparing for Milestone 1 Presentation

## Week 10 (11/03/2025 - 11/09/2025)
### Tasks
- Implement metadata extractor and metadata analyzer

### Completed
- Participated in team meeting and discussion regarding assigning tasks and code implementation updates
- Implement the base of metadata extractor and included tests

### Left to do
- Continue implementing metadata extractor (author for docx) and metadata analyzer

![Week 10](imgs/An%20Tran%20week10.png)

## Week 9 (10/27/2025 - 11/02/2025)
- Participated in team meeting and discussion regarding assigning tasks and code implementation updates
- Refactored file_classifier.py and text_preprocessor.py by adding variable and function input and output typings
- Added error handling to file_classifier.py and text_preprocessor.py
- Refactored file_classifier.py to use sets instead of lists, and altered inputs of isCode and isText
  - Updated file_classifier tests to match the new changes
- Reviewed PRs

All tasks assigned were completed this week
 
![Week 9](imgs/An%20Tran%20week9.png)

### Next week
- Implement metadata extractor and analyzer

## Week 8 (10/20/2025 - 10/26/2025)
- Participated in team meeting and discussion regarding assigning tasks and code implementation updates
- Adjusted file classifier and tree processor to not consider zipped files and drop invalid nodes (non-text or code files) from the tree
- Minor refactoring for naming conventions in the file classifier

![Week 8](imgs/An%20Tran%20week8.png)

## Week 7 (10/13/2025 - 10/19/2025)
- Participated in team meeting and discussion regarding assigning tasks
- Created getFileType function for file classifier and added tests which all passed
- Created PR for file classifier
- Reviewed PR #47

![Week 7](imgs/An%20Tran%20week7.png)

## Week 6 (10/06/2025 - 10/12/2025)
- Participated in team meeting and discussion regarding tasks and changes following finalized requirements
- Developed a list of tasks for this week
- Contributed to the WBS requirements table after finalized requirements

![Week 6](imgs/An%20Tran%20week6.png)

## Week 5 (09/29/2025 - 10/05/2025)
- Participated in discussions about DFD during the team meeting
- Collaborated on making the DFD
- Created PR template for merges to the dev branch

![Week 5](imgs/An%20Tran%20week5.png)

## Week 4 (09/22/2025 - 09/28/2025)
- Took part in team meetings and discussions about system architecture and project proposal
- Recorded meeting on system architecture discussion for future reference
- Contributed to making UML use case diagram
- Wrote two use cases and their corresponding requirements and test cases (browse timeline and view dashboard)
- Proofread and edited grammar mistakes for the project proposal

![Week 4](imgs/An%20Tran%20week4.png)

## Week 3 (09/15/2025 - 09/21/2025)
- Complete project requirements
Tasks done this week:

![Week 3](imgs/An%20Tran%20week3.png)
