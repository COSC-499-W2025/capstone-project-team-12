# Sithara Chari Personal Log (22066401)

## Term 2 Week 10 (03/09/2026 - 03/015/2026)
### TODOs:
- work on finetuning page
    - issue 498 and 499 https://github.com/COSC-499-W2025/capstone-project-team-12/issues/498 , https://github.com/COSC-499-W2025/capstone-project-team-12/issues/499 
- carry over from last week: address reviews on deduplication PR from 2 weeks ago concerning persistence of file set hashes
    - issue 481 https://github.com/COSC-499-W2025/capstone-project-team-12/issues/481
- change progress page from dark mode and light mode to match rest of the app 
### Work Done
- finished finetuning page 
    - pr links: #497, #500 https://github.com/COSC-499-W2025/capstone-project-team-12/pull/500 , https://github.com/COSC-499-W2025/capstone-project-team-12/pull/497
- finished refactor of deduplication 
    - pr #471 link https://github.com/COSC-499-W2025/capstone-project-team-12/pull/471

### What's next
- complete rework of progress page in time for peer review 
- link all pages to backend with api, as at least my pages currently are only static 

### Relfection
- I was able to get all my PRs in this week, except for the rework of the progress page which I just need to get done by peer review. It wasn't a very busy week, we had already gotten started on the frontend so it was just a matter of finishing as many pages as possible. Although we have not linked up the backend to all of our pages yet, I think the priority should be the UI and consistency between all the pages in time for peer review. 

![alt text](<imgs/Sithara Chari T2 Week 10.png>)

## Term 2 Week 9 (03/01/2026 - 03/08/2026)
### TODOs:
- Start working on a static progress page 
    - issue 458 https://github.com/COSC-499-W2025/capstone-project-team-12/issues/458
- address reviews on deduplication PR from last week concerning persistence of file set hashes
    - PR 438 link: https://github.com/COSC-499-W2025/capstone-project-team-12/pull/438 
### Work Done
- finished coding and testing for the progress page

### What's next
- finish and make PR for deduplication refactor
- work on more pages for frontend 
- start to connect API to frontend 

### Relfection
- This week I had not much work to do, both my tasks were relatively small, but I wasn't able to finish both my tasks, so I just focused on finishing the page that I had to. There were some miscommunications and inconsistencies with the UI color scheme, mainly if we were doing light mode or dark mode, but we will get that sorted out in our meeting on monday. 

![alt text](<imgs/Sithara Chari T2Week9.png>)



## Term 2 Week 6, and 8 (2/9/2026 - 3/1/2026)

### Week 6 work done:
- Reworked how filepaths were being compared when an incremental file was being uploaded (when an anaylsis was being updated) 
    - Issue 401 https://github.com/COSC-499-W2025/capstone-project-team-12/issues/401

### Week 8 work done: 
- Implemented additional endpoints for deleting items from the database such as protfolios and resumes and added intergration tests for them 
    - issue 430 https://github.com/COSC-499-W2025/capstone-project-team-12/issues/430
    - issue  445 https://github.com/COSC-499-W2025/capstone-project-team-12/issues/445
- completed the milstone requirement of recognising duplkicate files and only maintaining one in the system 
    - issue 437 https://github.com/COSC-499-W2025/capstone-project-team-12/issues/437
- updated the readme file with link to the test files TAs can use to test our system and added specific instructions for when they run the app.
    - isseu 447 https://github.com/COSC-499-W2025/capstone-project-team-12/issues/447

### Next week: 
- Start working on frontend, possibly edit backend some more if anything we hadn't thought of completely comes up 

Reflection: 
- this week was very rushed, with the presentation on Wednesday, and me only starting to code after that. It felt like taks just kept getting added, which is why I had 4 PRs this week alone (which is more than I usually have), but we were all rushing to finish things up for milestone 2 so it makes sense. 

![alt text](<imgs/Sithara Chari T2 Week 8 Logs.png>)

## Term 2 Week 4 and 5 (01/26/2026 - 02/08/2026)
### TODOs:
- Refactor API setup that was done in week 2 to be in accordance with SRP 
    - issue 363 https://github.com/COSC-499-W2025/capstone-project-team-12/issues/363
- Start working on milestone requirements for incremental file analysis along with Sara and Devin, starting with reworking certain things in our file manager, and creating modules to handle tree from different points in time of the same file path. 
    - issue 326 https://github.com/COSC-499-W2025/capstone-project-team-12/issues/326 
    - issue 349 https://github.com/COSC-499-W2025/capstone-project-team-12/issues/349 
    - issue 353 https://github.com/COSC-499-W2025/capstone-project-team-12/issues/353 
### Work Done
- finished all the TODOs that I had
- coordinated with Sara to figure out how to implement incremental file handling
- Wrote code and tests for my tasks 
- Made PRs, made requested changes and reviewed and requested changes on teammates PRs

### What's next
- Change the way we compare and validate file paths when updating a previous analysis (incremental file thing) as was pointed out in Sara's review of my PR 
- work on handling duplicates of files (milestone req #22)
- work on issues brought up during peer testing 

### Relfection
- I was very unsure of how to implement the incremental feature, even though I had discussed it with my teammates, mainly Sara, many times, so I kept procrastinating implementing it, which ended up in me putting up a PR only Saturday night, which goes against our groups agreement of having PRs up by thursday so we can have time to review and make changes. This PR was also more than 500 lines, which in a recent announcement our TA said that larger PRs will be penalized, however for this particular feature, it affected so many other modules as it changed the way file_manager.py did certain things, which is the base of our entire project, so it had many waterfall effects which I feel justifies a large line count. 

![alt text](<imgs/Sithara Chari T2Week4.png>)

## Term 2 Week 3 (1/19/2026 - 1/25/2026)
- No work done this week due to personal issues

## Term 2 - Week 2 (01/12/2026 - 01/18/2026)

### TODOs
- Setup API for communication between frontend and backend (requirement 31 and 32)
    - issue 312 https://github.com/COSC-499-W2025/capstone-project-team-12/issues/312 
    and 313 https://github.com/COSC-499-W2025/capstone-project-team-12/issues/313 
    

### Work done
- Finished issues 312 and 313
    - Finished writing code and tests for the initial implementation of API using FastAPI
- Reviewed several PRs that were up this week (PR numbers: 16, 309, 308, 300, 293)

### What's Next
- Continue to work on API, modify code so it maintiains SRP
- Start working on milestones 21, 22, 33, 34

### Reflection
- During our team meeting on Monday, An and I had planned to share requirements 21 and 22, but we only got more confused as we discussed it within ourselves, so when we brought it up with the rest of the team, we decide to split it for next week and so I had taken over doing the API setup for this week. Despite the task only being assigned on Wednesday, I was able to finish the setup and test for it as well. Although I wasn't able to implements all the changes that were requested on my PR. 

![alt text](<imgs/Sithara Chari T2Week2.png>)

## Term 2 - Week 1 (01/05/2026 - 01/11/2026)

### TODOs
- Refactor num_topic logic in topic_vectors.py: make it so that it is scaled according to the number of documents (issue # 271) and the corresponding tests (issue # 272)
- Work with An on requirements 21 and 22 

### Work done
- Finished refactoring num_topic (issues 271 and 272)
- participated in team meeting to decide what to work on this week 
- reviewed PRs 

### What's Next
- Start working on milestone #2 requirements 
- continue to improve the logic we have now (further optimization of topic modelling)

### Reflection
- We had our team meeting on wednesday instead of the usual monday, which lead to a lot of the work this week being rushed, so I wasn't able to start on milestone #2 requirements, but from this coming monday we'll be back to our routine of having our meeting on monday and then making sure initial PRs are in by thursday, giving everyone plenty of time to review and request changes. 

![Type of tasks I worked on](<imgs/Sithara Chari Week 15.png>)

## Week 3 (09/15/2025 - 09/21/2025)
- Contributed to functional and non-functional requirements
- Took part in collaborative team discussions regarding requirements with other teams
![alt text](<imgs/What types of tasks did you work on this past sent Check ALL Flat apply, When you are done, take a screenshot of this question w.png>)


## Week 4 (09/21/2025 - 09/28/2025)
- took part in team discussions regarding software architecture and the project proposal 
- Wrote our project solution in the Project Proposal
- Participated in class discussion with other groups 
- Wrote the inital use cases for our proposal, before we restructured our software architecture
![alt text](<imgs/Sithara Chari Week 4.png>)

## Week 5 (09/29/2025 - 09/25/2025)
- took part in team discussions regarding DFDs and future plans for project 
- contributed to making the level 0 and 1 DFDs
- Participated in class discussion with other groups 
- Made issues in our kanban board of all the things to do this week 
![alt text](<![alt text](imgs/Sithara Chari Week 5.png)>)


## Week 6 (10/06/2025 - 10/12/2025)
- Performed code reviews for PR's in the project
- Participated in team meetings to discuss changes to architecture, DFD, and WBS
- Wrote first draft of our file manager code
- Submitted PR for code 
- Sade requested changes
- Researched how to use Pathlib library in python 
![alt text](<imgs/Sithara Chari Week 6.png>)

## Week 7 (10/13/2025 - 10/19/2025)
- Performed code reviews for PR's in the project
- Participated in team meetings to discuss changes to existing code, as well as what to do moving forward
- Made requested implementation changes to file manage (issue #40)
- Made new PR
![alt text](<imgs/Sithara Chari Week 7.png>)

## Week 8 (10/20/2025 - 10/26/2025)

### Work Done
- attended team meeting, talked about how all our code fits with each others work and how to make it better 
- refactored file_manager code according to notes from meeting
- filled Lexi in on what she should do as she couldn't attend the meeting, and she needed to work off of my file_manager class
- coordinated with other teammates about what my class returns and what their classes expect so that everything matches 
- performed PR reviews 

![alt text](<imgs/Sithara Chari Week 8.png>)


### Review
Overall this week we mainly focused on refactoring our existing code, so we have everything we need moving forward. I couldn't get all the refactoring done for this week, so more will be happing in the following sprint.

### Future Plans
- refactor the nodes further: instead of storing binary data in the nodes directly, store in an array and have the index in the node
- add pytests for file_manager 

# Sithara Chari Personal Log (22066401)

## Week 9

### Work Done

- Attended and participated in team meeting for plans for this week
- Added types to all function parameters and return variables for easy error handling
- Stored binary data in a separate array instead of in the nodes itself for lighter data 
- added a function to be able to retrieve binary array without calling file manager again 
- Reviewed and requested changes for peers' PRs
- Refactored attribute names so they are consisten across class 

![alt text](<imgs/Sithara Chari Week 9.png>)

### Review and future plans

- Was also supposed to do testing for file manager, but I was not able to get that done this week so it will probably be pushed to next week 
- Next week we also make our own custom nodes separately, as it is now done in file_manager itself which is doesn't make much sense 


## Week 10
## TODOs
- File manager testing (issue #92)
- get consent from user to access their files
- start processing bag of words (BOW) to generate topic vectors with pyLDAvis ML model 

### Work Done 
- Participated in team meeting, prioritized taks to complete with a more focused path towards milestone 1
- Wrote pytests for file_manager.py (issue #92)
- Edited file_manager.py to reflect new changes that came out during testng process 
- Reviewed teamates PRs
- Researched how to use pyLDAvis for our exact purposes

![alt text](<imgs/Sithara Chari Week 10.png>)

### Review and future plans 
- This week I was really busy with my midterms, so I only was able to do the file manager testing and not any of the other work I was supposed to do 
- I will finish the ML implementation, and keep working on our anaysis pipeline. 


## Week 11 and 12
## TODOs
- topic vector generation and testing (issue number 150 and 164) using gensim topic vectors
- Integrate all components into main.py which is the entrypoint to our app

### Work Done 
- Participated in team meeting, prioritized taks to complete with a more focused path towards milestone 1
- researched how to use gensim to generate topic vectors from our bag of words.
- Wrote code for generating topic vectors using gensim
- Reviewed teamates PRs

![alt text](<imgs/Sithara Chari Week 12.png>)


### Review and future plans 
- I finished most of the analysis with topic vectors during the reading week, and I finished writing the test for it earlier this week. 
- I didn't have time to work on main.py so that will be done next week mostly 
- Next week since we have no more new components to code, we will just polishing up everything we have and storing everything in the db, and getting ready for the presentation.


## Week 13
## TODOs
- Integrate all components into main.py which is the entrypoint to our app

### Work Done 
- Participated in team meeting, prioritized taks to complete with a more focused path towards milestone 1, which was mainly refactoring and integration
- spent a lot of time debugging code, and reviewing teammates PRs
- Finished integrating main.py all the components and made it more user friendly (issue # 233)
- Requested and stored user consent for future use. (issue # 234)

![alt text](<imgs/Sithara Chari Week 13.png>)


### Review and future plans 
- We found a lot more bugs in our code than we epxected, so a lot of time was spent trying to get those fixed so that we had a working app 
- continue to work on the presentation 


## Week 14
## TODOs
- Work on the presentation 
- Remove any bugs in app

### Work Done 
- Participated in team meeting where we rehearsed for our team presentation 
- Delivered team presentation 
- Fixed testing bug (issue # 249 )
- Reviewed teammates code
- Helped briefly in figuring out the Mac vs Window bug (issue # 250)
- Finished writing out the team contract
- Helped in editing our Milestone #1 video 

![alt text](<imgs/Sithara Chari Week 14.png>)



### Review and future plans 
- Continue to work on anything I can during the winter holidays for bonus
- No other future plans as of now, we will start planning again once the next semester starts. 



