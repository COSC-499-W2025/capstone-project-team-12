# Lexi Loudiadis (93546844) Personal Log

## Week 14 (12/01/2025 - 12/07/2025)

- I discovered a Mac vs Window bug while running a teammates' PR last week  This week we addressed this problem and after many long hours we got to the bottom of it
- Implemented the functionality to upload files from a user's computer - prior to this we could only test using repos/files already in the container
- Created tests for Maddy's project analysis database integration and display results PR
- Milestone 1 presentation and preparation
- Team meetings, dividing the final tasks left to do for Milestone 1

### In Progress
- Currently we are just finishing our deliverables for Milestone 1 and then will likely all be taking the break off

### What's Next
- After winter break we will meet to figure out how to approach the next milestone

### Reflection
- Although we are mostly happy with how our MVP turned out, we did feel we ended up with a lot to get done in the last 2-3 weeks. As a result, we would like to ensure that we go through all the requirements for Milestone 2 during the first week of class in January, and map out what needs to get done and when. This will help make sure we are not pressed for time at any point and we all know exactly what needs to get done

![Type of tasks I worked on](imgs/Week%2014%20Lexi.png)

## Week 13 (11/24/2025 - 11/30/2025)

- Finished the implementation of our project analysis, which uses import lines to extract skills in Git repos. Ensure milestone requirements were satisfied. Included relevant testing
- Reviewed teammates' PRs and helped debug issues that arose due to integration of different modules in our backend entrypoint
- Participated in writing the team contract
- Working on our slide deck

### In Progress
- While reviewing Maddy's PR I discovered a bug in how Mac computers are handling files. We discovered that, while the OS on my Mac was seeing the .git file in our test repo, somehow this file was getting dropped from the node when running our pipeline. As a result, PyDriller could not extract commit info since it requires a .git file. Maddy and I have been working on debugging this and will continue resolving this issue early next week.  

### What's Next
- Preparing for our presentation
- Continuing to debug and test for our M1 deliverable

### Reflection
- All work planned for this week was accomplished, and some additional testing and debugging was done on other teammates' PRs to ensure integration was going well.

![Type of tasks I worked on](imgs/Week%2013%20Lexi.png)


## Week 12 (11/17/2025 - 11/23/2025)

- Addressed a circular imports bug that ended up in our main branch
- Did some refactoring to promote loose coupling by ensuring different modules do not talk to each other directly and are instead called from main
- Worked on the project analysis pipeline; added methods so that we can rank importance of projects and summarize the top ranked projects
- Wrote tests to test these methods

### In Progress
- Figuring out how to deepen project analysis and differentiate between portfolio and resume insights

### What's Next
- Next week I will work on extracting the import lines from projects, which will be used to extract key skills, produce a chronological list of skills, and differentiate between code files and test files
- Additionally I will help ensure that everything is running cohesively for our demo and deliverable

### Reflection
- This week I was the only one who wasn't continuing to work on something that I'd worked on in previous weeks, so during the team meeting I asked who needed help and that's how I ended up working on the project analysis pipeline with Maddy. We met on Thursday to discuss what was left to do to ensure that we hit all the M1 requirements and how to split the remaining work. There is still a bit left to be done as outline above, which will be done early next week. However, all work I planned for this week was completed

![Type of tasks I worked on](imgs/Week%2012%20Lexi.png)



## Week 10 (11/03/2025 - 11/09/2025)

- Implemented the BoW Cache, which stores and retrieves tokenized text before text analysis, given a hash key
- Implemented unit tests for the BoW Cache
- Investigated problems with path and environment configurations that was causing tests to fail and unexpected output
- Did code reviews for my teammates' PRs
- Took part in team meetings to discuss our work for the coming week and to talk more about our upcoming Milestone 1

### What's Next
- There ended up being a logic error in with my hash key, in which the current repo_id is derived only from the file path, which means that updates to files aren't detected if the file location doesn't change (and therefore the system reuses outdated cached data). Tentatively the plan to fix this is to incorporate something like a file modification timestamp or something that might require our fully functional metadata extractor, but at the very least I will look into a solid bug fix next week.
- We did not manage to get our text analysis pipleine with an ML model done this week, but I am hoping we will get it done next week so that we can start moving onto our analysis ASAP. And now that I am done the BoW Cache (minus the bug) I can lend a hand to the teammate who was assigned to work on it this week 

### Reflection
- My assigned tasks this week were implementing the BoW Cache and testing the BoW cache, which I completed

![Type of tasks I worked on](imgs/Week%2010%20Lexi.png)


## Week 9 (10/27/2025 - 11/02/2025)

- Researched for the PII Remover
- Coded the PII Remover
- Wrote local and unit tests for the PII remover
- Reviewed teammates' PRs
- Participated in team meetings 

### What's Next
- TBD but we will likely keep making progress on the metadata analysis pipeline that was started this week. Additionally some of us may also start working on the text analysis pipeline using a ML model. We also will have to make the corresponding changes to our main method to ensure that we can run our existing pipelines from it.

![Type of tasks I worked on](imgs/Week%209%20Lexi.png)


## Week 8 (10/20/2025 - 10/26/2025)

- Coded the main.py method
- Refactored the validate_path() logic
- Wrote unit tests for the validate_path() method

### In Progress

- Adding more logic to main as it what we're using to handle interaction between different classes for Milestone 1. So we need to keep connecting it to different classes/methods as they become available. For next week this is likely connnecting it to Text Preprocessor, our newly refactored File Classifier and our newly added Code Preprocessor. 

### What's Next
- Some more refactoring, establishing testing, var/func name standards, type declarations, etc
- Implementing our PII remover so the Text Preprocessing pipleine is fully completed

![Type of tasks I worked on](imgs/Week%208%20Lexi.png)


## Week 7 (10/13/2025 - 10/19/2025)

- Coded the text tokenizer
- Coded the text stopword remover
- Coded the text lemmatizer
- Created tests for these which including edge cases to make sure they'll work as expected
- Reviewed comments on my PR and made changes accordingly

![Type of tasks I worked on](imgs/Week%207%20Lexi.png)

## Week 6 (10/06/2025 - 10/12/2025)

- Wrote the DFD explanation for our README
- Wrote the System Architecture explanation for our README
- Revised our DFD diagram to make it consistent with the new project requirements
- Attended group meetings and participated in discussions

![Type of tasks I worked on](imgs/Week%206%20Lexi.png)

## Week 5 (09/29/2025 - 10/05/2025)

- Participated in team discussions about our DFD Level 0 and Level 1
- Did research to better understand our software architecture
- Helped create and edit our DFD diagrams
- Participated in class discussion with other groups

![Type of tasks I worked on](imgs/Week%205%20Lexi.png)


## Week 4 (09/22/2025 - 09/28/2025)

- Participated in team discussions about our software architecture and project proposal
- Wrote up parts of the project propsal
- Contributed to the UML use case diagram
- Participated in class discussion with other groups

![Type of tasks I worked on](imgs/Week%204.png)


## Week 3 (09/15/2025 - 09/21/2025)

- Contributed to team discussions for project requirements
- Drafted functional and non-functional requirements
- Engaged in discussion with other groups regarding the requirements we came up with

![Type of tasks I worked on](imgs/Lexi%20Loudiadis%20Week%203.png)

