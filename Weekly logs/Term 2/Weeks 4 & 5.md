# Term 2 Weeks 4 & 5 (01/26/2025 - 02/08/2025)

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
- Refactored LLM clients
  - created a new simplified an unified client to get rid of code duplication
  - Separated prompt from LLm file for easier manitainability and accessibility
  - Updated all LLM related tests
- Implemented the portfolio feature. The portfolio generated showcases in-depth project information and compares projects with metrics like skills progression, collaboration evolution, and role progression.
- Implemented the portfolio editing feature - after the user generates the portfolio, they are asked if they want to edit before saving (note the saving functionality is still a work in progress). Portfolio sections available for editing include project details and skills & technologies
  - Wrote extensive tests for these features
- Updated logic for how contributors in a GitHub project are counted
  - Also privatized the PII for these contributors to ensure no data is being stored unnecessarily
- Updated the logic for editing resumes to allow the user to edit the text that was previously generated instead of forcing them to always completley replace the section they want to edit
  - Also utilized helper methods to ensure that editing is consistent across all parts of the resume
  - Made date validation more robust
  - Added testing for this implementation and updated previous versions to support the new implementation
- Refactor API setup that was done in week 2 to be in accordance with SRP
- Started working on milestone requirements for incremental file analysis, starting with reworking certain things in our file manager, and creating modules to handle tree from different points in time of the same file path.
- Completed Analysis extractions and resolved merge diffs from last 2 weeks
- Edit dockerization to live mount codebase to enable faster dev time
- Edit PII remover to not have spacy-model-lg as dependency and use predownloaded spacy-sm model instead
- Integration Testing of primary analysis pipeline
- Project management, updated dates, priorities and size information for ~200 Team items (recent and old) that lacked this tracking
- Finished and wrapped up all new DB schema rework related changes
- Participated in and ran stations for peer testing


### Burnup chart & Task Table
![T2 Weeks 4 & 5 Burn Up]()


![T2 Weeks 4 & 5 Tasks Table]() 
Filtered to only show Tasks with changes this week. We had to use this format due to issues not linking to dates in "Completed Tasks".

### Test Report
![Term 2 Weeks 4 & 5 Test Report](/imgs/T2%20Week%204%20&%205%20Test%20Report.png)

### In Progress
- Getting portfolio to be saved to the database.
- Incorporate evidence of success
- Completing the integration testing of the primary analysis pipeline for metadata analysis and database saving/retrievals

### Upcoming plans
- Change the way we compare and validate file paths when updating a previous analysis
- work on handling duplicates of files
- work on issues brought up during peer testing
- Complete the implementation of storage of the resume to the database
  - Slight refactor of how the user will access and edit this functionality, we want to generate a resume as soon as a new analysis is completed and allow a user to view all versions of a resume attached to an analysis
- Finalize our API endpoints
- Ensure we have completed all tasks to satisfy the Milestone 2 requirements

### Reflections
- Following the peer testing, we were able to find some changes to be made to the system to improve the overall usability. The most eye-opening part was how people responded to the amount of information that is provided during the analysis. We have added a lot of options for users to customize this analysis, but we also were printing everything that was being extracted and compiled for users to view and it led to some people being overwhelmed by the amount of information provided. Going forward we are looking to remove some of this additional clutter from the analysis steps so that it is easier for the user to determine what is happening in the analysis, and what their changes actually mean.
- Overall, we are making strong progress toward completing the requirements for Milestone 2. We continue to meet regularly and although some of our tasks are tightly coupled with each other, we have been able to ensure the overall functionality of our system is continuing to improve. 
