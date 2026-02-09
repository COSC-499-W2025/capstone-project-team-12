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



### Burnup chart & Task Table
![T2 Weeks 4 & 5 Burn Up]()


![T2 Weeks 4 & 5 Tasks Table]() 
Filtered to only show Tasks with changes this week. We had to use this format due to issues not linking to dates in "Completed Tasks".

### Test Report
![Term 2 Weeks 4 & 5 Test Report](/imgs/T2%20Week%203%20&%204%20Test%20Report.png)

### In Progress
- Getting the resume and portfolio to be saved to the database.
- Incorporate evidence of success 

### Upcoming plans
- Change the way we compare and validate file paths when updating a previous analysis
- work on handling duplicates of files
- work on issues brought up during peer testing
- Complete the implementation of storage of the resume to the database
  - Slight refactor of how the user will access and edit this functionality, we want to generate a resume as soon as a new analysis is completed and allow a user to view all versions of a resume attached to an analysis
- Finalize our API endpoints
- Ensure we have completed all tasks to satisfy the Milestone 2 requirements

### Reflections
- 
