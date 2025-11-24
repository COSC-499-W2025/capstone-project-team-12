# Week 12 (11/17/2025 - 11/23/2025)

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
- Implement metadata metadata analyzer
- Finish implementing author extraction in metadata extractor
- Implemented the local llm and containerized it into docker
- Added local-llm.dockerfile for an Ollama Phi-3 Mini container
- Updated docker-compose with a local_llm service, memory limits, and a persistent volume
- Wrote tests for the local implementation of the llm
- Addressed a circular imports bug that ended up in our main branch
- Did some refactoring to ensure different modules do not talk to each other directly
- Added methods so that we can rank importance of projects and summarize the top ranked projects
- Completed the extraction of Git contribution metrics, and removed potential pieces that could include PII (commit messages)
- Added testing for Git Contribution extraction
- Implement method to create a timeline of all project repositories from the user
- Implement analysis to find the rank of a user in a project
- Calculate code vs test ratio for projects
- Setup and wrote initialization for database
- Fixed Docker bad config leading to high build times
- Added dates for numerous issues and PRs in Github Proj
- DB Access util functions module
- Component Testing for DB Utils Module
- Wrote code for generating topic vectors using gensim
  
### Burnup chart & Task Table

[//]: # "ADD IMAGES after all the work is pushed"

![Week 12 Burn Up](/imgs/Week%2012%20Burnup.png)

![Week 12 Tasks Table](/imgs/Week%2012%20Team%20Tasks.png)
Filtered to only show Tasks with changes this week.

### In Progress
- Continuing to brainstorm how to deepen analysis and provide portfolio specific outputs

### Upcoming plans
- Get out MVP in order for Milestone 1
- Potentially set up CI/CD
- Finish project analysis pipeline
- Integrate all components into main.py, our backend entrypoint

### Reflections
- This was a very productive week for us, we were all motivated by the upcoming Milestone 1 deadline
- The team was very driven to produce work that corresponds with M1 project requirements and make sure we have our MVP finished for next week
- We had an extra meetting this week to make sure we are all on the same page technically speaking as we finish our components
