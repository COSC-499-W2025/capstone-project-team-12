# Sara Srinivasan Personal Log (10801751)

## Term 2 Week 3

### Work Done

- Note my contributions for this week are not merged to main as it is blocked by some other PRs that needed to be merged and resolved first.
- Additionally DBschema rework mandated a rework of the primary analysis pipeline as the function was ~350 line bulky coupled mess.
  See Draft PRs  [#342](https://github.com/COSC-499-W2025/capstone-project-team-12/pull/342) and [#343](https://github.com/COSC-499-W2025/capstone-project-team-12/pull/343) for WIP commits and code changes for both of the above respectively.
- Designed Created new DB schema and associated rework.
  - Both Devin and Sithara's Tasks for the week are based on this new design
  - Explained to team new design an appropriate use of new db using design mocks
- Extracted and simplified functionality of analysis pipeline
- Helped Sithara and devin with implementation of db manager rework and file tracking reworks
- Commented and reviewed PRs 

### Quiz Response

![Term 2 Week 3 Quiz Response](imgs/Sara%20Srinivasan%20T2%20Week%203.png)

### Review and Plans

Unfortunately my work was blocked by other PRs that needed to be merged first, the contributing factors were that the team members were busy and occupied with other classes and simply the scale of the rework, drastically affecting numerous modules. Next week will likely be a team effort to complete,test and merge this rework!

## Term 2 Week 2

### Work Done

- Participated in team meeting and helped decide on tasks and priority for this and next week
- Helped An to rework/redesign tree managemant and fileclassifier
- Discussed rebuild of DBschema and downstream modules for next week to enable incremental changes
- Implemented ability to associate thumbnail to a particular analysis (Feature and testing)
  - Edit DB Schema
  - Edit Prompting in main
  - New validation function
  - New DBmanager class function
  - Tests for above
- Implemented testing for Code-Preprocessor module (testing)
- Requested changes and approved other's PRs


### Quiz Response

![Term 2 Week 2 Quiz Response](imgs/Sara%20Srinivasan%20T2%20Week%202.jpg)

### Review and Plans

Thumbnail implementation needs more interactivity to help the user determine if image was added successfully
Next week Myself,Sithara and Devin are reworking the DB schema from the ground up and making necessary downstream changes to 
implement incremental tracking of not just data but also files and to store multiple versions of resumes and portfolios.

## Term 2 Week 1

### Work Done

- Participated in team meeting
- Helped extract input validation and execution logic from main
- Requested changes and approved other's PRs
- Composed weekly log for this week (rotating responsibility, by week)

### Quiz Response

![Week 12 Response](imgs/Sara%20Srinivasan%20Week%2013.png)

### Review and Plans

Productive week for personally, assuming the last couple bugs get squashed before sunday deadline
All that is left is to tie up a few loose ends in the repo. Prepare and deliver the presentation.

## Week 13

### Work Done

- Led discussion of tasks for week and assigned tasks during meeting
- Establish plan for team to follow throughout the week
- Reworked text preprocess and code preprocess as pre-step to integration
- Reworked testing for both of the above to match new functionality
- Investigated and fixed difficult bugs and cleared up misunderstandings regarding component roles
- Contributed to shared team slides
- Prepared with team for presentation.

### Quiz Response

![Week 12 Response](imgs/Sara%20Srinivasan%20T2%20Week%201.png)

### Review and Plans

Productive week for personally, assuming the last couple bugs get squashed before sunday deadline
All that is left is to tie up a few loose ends in the repo. Prepare and deliver the presentation.


## Week 11 and 12

### Work Done

- Dev-Ops
  - Setup and wrote initialization for database
  - Fixed Docker bad config leading to high build times
  - Added dates for numerous issues and PRs in Github Proj
- Code
  - DB Access util functions module
  - Component Testing for DB Utils Module
  - Component Testing for Code Proproccessor
- Attended weekly meeting
- Helped team decide on ways to deepen analysis
- Discussed with Devin details regarding local llm implementation
- Added Start and End Dates to many issues that were not properly configured in Github Project
- Tested and Commented on Team Member's PRs

### Quiz Response

![Week 12 Response](imgs/Sara%20Srinivasan%20Week%2012.png)

### Review and Plans

Final stretch for Milestone one Completion, Lots of work done over this week.
Should be able to focus on integretion for Week 13
Personally I am considering setting up github workflows CI/CD next week since we have an MVP
(Discuss with team next meeting)

## Week 10

### Work Done

- PR reviews
- Helped address tech issues of team members
- started work on code preproccessor testing

### Review and plans

Not a great week for me between midterms and mental health concerns. Hopefully I can make up for it over reading break.

## Week 9

### Work Done

- Swapped Spacy based pipeline to gensim due to upstream errors
  - Docker edits
  - Text preprocessor edits
  - Code preprocessor edits
- Rework text pre process to use chaining instead of nested function calls
- Implement comprehensive pytest testing for text preprocess
- Made github tasks
- Involved in reviews, help and feedback
- Led and provided crucial input in PII removal implementation

![Week 9 Response](imgs/Sara%20Srinivasan%20Week%209.png)

### Review and future plans

- New Sprint structure to accomodate Lexi's work styles
- Bigger progress steps to have MVP before Nov 30
- Finish Code preprocess testing early in week 10
- Join Maddy in Github repo analysis
- Start ML implementation

## Week 8

### Work Done

- DevOps(Mon/Tue)
  - Troubleshoot postgres dockerization
  - Test Locally the use of Dev Containers
  - Teach Team to use Dev Containers
  - Added locally mounted volume directory for data persistence
- Coding (Wed - Sun)
  - Documented and discussed with team use of Pygments and related concerns
  - Composed and wrote entirety of code pre_processing component (incl. comments and error handling) ~180 lines
  - Reviewed PRs
- Github Process
  - Made all issues and project Tasks for the week (Mon)
  - Tracked and updated github project and timeline for team

![Week 8 Response](imgs/Sara%20Srinivasan%20Week%208.png)

### Review and Future Plans

Very productive week for me, i'd argue it makes up for last week's absence (though that was for medical reasons...)

One of our dependencies (SpaCy) is broken due to upstream changes, I've volunteered to investigate and fix the issue or alternatively find an alternative library.

This will require a full rewrite of one of our text_processing module. Which I am likely to handle next week as well

We found the current agreed upon coding style standards to be inadequate so we're planning to discuss a full rework
of our code base next week to bring all components into alignment

A conversation I will likely lead, with that all of our preprocessing components are done.
We should be well positioned to get into ML driven Analysis in Week 10

## Week 7

### Work Done

- Made minor updates to Github Project.
- Reviewed PRs and other's code and suggested changes.
- Helped provide feed back and addressed implementation concerns and questions on Discord
- Assigned tasks to team

![Week 7 Response](imgs/Sara%20Srinivasan%20Week%207.png)

### Review

Personally had to deal with a ton of disassociative stress and persistent brain fog. Didnt get a whole lot done this week.

### Future Plans

- Review and rework testing for file manager component.
- Finish db - persistence for dockerization
- Begin (and hopefully complete) work on Code pre-process pipeline

## Week 6

### Work Done

- Made edits to Architecture diagram based on finalized requirements list
- Added TA's Pull-Request Template to Repo
- Dockerized frontend, backend and database
- Made edits and reworked DFD level 1 based on new requirements
- Edited,modified and reformatted the DFD and Arch diagram explanation by Lexi
- Provided input on comments for the requirements table.
- Created updated and managed tasks in Github Projects
- Made PRs for various changes
- Helped Troubleshoot docker deployment issues on Devin's computer.

![Week 6 Response](imgs/Sara%20Srinivasan%20Week%206.png)

### Review and Future plans

Very productive week for the team. The end of design phase is in sight QwQ.

- Add Docker volumes and make db data persistent
- Begin code work on project

## Week 5

### Work Done

- Discussed and helped with DFD level 1 and 0
- Suggested changes for DFD
- Discussed with other teams, their DFDs
- Added and managed github project tasks (partially)
- More progress on PR automation, one more step remaining for completion
- Opened PR for DFD addition

![Week 5 Question response](imgs/Sara%20week%205%20question%20response.png)

### Review and Future plans

Had a medical flare up that took priority, team accomodated and helped make up for my relative decrease in contributions

## Week 4

### Work Done

- Participated and lead discussions on architecture
- Participated and lead discussions on work division based on architecture
- Researched and learned various classical NLP methods
- Researched libraries and decided on tentative tech-stack + libraries
- Created New Architecture diagram based on new LDA Topic Analysis Approach
- Minor contribution and edits to use cases section of Project Proposal
- Created and populated Github Project
  - Resolved team repo attribution issues
  - Remade all issues/task from scratch as fix
  - Coordinated with Team-8 to correct misattributions
- Began work on PR Templates and automation
- Provided help and insight on use-cases
- Made live presentation and elaborated on Architecture and diagram
- Found, curated and provided selective and relevant resources for team learning on Topic Identifying MLs

![Canvas quiz response](imgs/Sara%20Srinivasan%20Week%204.png)

### Review and Future Plans

Populate the rest of the Github Project with foreseeable tasks  
Complete work on PR automation

## Week 3

### Work Done

- Contributed to Functional requirements and non-functional requirements
- Added User requirments section to requirements doc and filled it out
- set up inital repo and file structure
- set up team discord for communication and organization
- created 'logs' branch
- discussed and contribured SOP for team and github use
- discussed and agreed upon weekly meeting times

![Response to question on team eval](imgs/Sara%20Srinivasan%20Week%203.png)

### Review

We have good team synergy and a shared line of thinking with enough diversity in skillset that I feel confident in our team's ability to work together. We had some issues with pushing directly to main by accident since we cant setup branch protection on a non enterprise private repo. Hopefully it shouldnt happen going forward
