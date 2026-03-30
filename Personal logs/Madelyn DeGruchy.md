# Madelyn DeGruchy Personal Log (85064962 - maddydeg)
## Term 2 Weeks 11 & 12 (03/16/2026 - 03/29/2026)
- Updated the backend for the resume generation and display
    - Updated LLM prompt so to not include any references to topic vectors
    - Updated Resume Dict to allow for the saving of LinkedIn, phone number, Education, Awards, and previous work experience
    - Separated the generated summary in to a list of strings to make it easier to separate them for display on the front-end
- Updated the front-end to include the work experience, awards, education, linkedin, and phone number. This allows the user to populate these sections in the database. This included tweaking the API call to ensure everything was being sent back to the database in the same format.
- Added testing for the above functionalities.
- Added the ability to edit Portfolios that have been generated. Implemented the corresponding API call. Needed to add a wrapper due to type mismatch between the portfolio display in the front-end and the database strucure.
    - Added testing for this edit functionality
- Implemented the export functionality for the resume
    - Supports docx and pdf format
    - Added a resume preview modal so the user is able to see what the formatting will look like for the professional resume
    - Pass the username and email from onboarding to the resume to be displayed at the top of the users resume.
    - Added relevant testing
- Added length enforcement to the resume
    - Added character limits, entry limits (number of awards, etc), and bullet point limits. This is to encourage the user to keep their resume readable. We do allow the user to exceed the character limit with a visual warning that they have gone over so that they still have the ability to customize this resume as they see fit
    - When they preview the resume, they will receive a warning if they have gone beyond a single page. It includes a percentage of how far beyond 1 page they've exceeded, and a red line appears on the preview at the one page cut off point.
    - Slight refactoring of how we export to try and resolve a scaling issue. docx is tricky to get formatted correctly, so we display a disclaimer to the user that for a more consistent export, use pdf.
 
## Next Week
Project voting! 
 
## Reflection
Losing teammates near the end of the semester applied some pressure to ensure we met the Milestone 3 deadline. Although there are some features and components that I had hoped we would get to that ultimatley had to be left as known bugs or potential future additions, I am proud of the team for perservering through the last few weeks. I am looking forward to looking at more of our classmates projects as we head in to project voting. 

![Peer Evaluation Term 2 Weeks 11 & 12](imgs/Madelyn%20DeGruchy%20T2%20Week%2012.png)

## Term 2 Week 10 (03/09/2026- 03/15/2026)
- Updated our backend to now support storing information related to awards, education, and previous work experience for the resume. They are user-populated fields from the front end. (PR #486)
    - Included some minor refactoring of the LLM prompt and generated summary list to make the display cleaner on the front end.
    - Updated testing to ensure overall functionality worked as intended and to resolve tests that now failed
- Updated the front-end to make calls through the API to display resumes and to add sections for the education, awards, and previous work experience sections. (PR #487)
    - Now once the user has created a resume from an analysis, they are able to view it from the resume page, make edits, and once they save this new version it will update the database so the changes persist
    - Added relevant testing for these frontend changes PR #502
- Participated in team meetings and code reviews

## Next Week
- Need to check with the team on how we want to work with the router, as this will impact how the resumeId will be passed to the page to display. Currently we only access the resume page as part of the initial analysis flow, where it is generated upon the first completion of an analysis. When the user goes to access the page later on, it will likely not have the sidebar, and we will need to likely make use of a router.
- Prior to Wednesday's class we will need to make some final touches to ensure the basic flow of our system is in tact and ready for peer review. 

## Reflection
- Some teammates have had personal issues arise in previous weeks that had left me slightly worried we would not be able to stay on track for Milestone 3 completion given the tight turn around. Overall, the team has handled it very well and I believe that we will be able to have a final product ready for the Milestone 3 presentation and demo in the coming weeks. I also had a busy week with my work and was behind schedule for getting my testing up for the team, so I am looking to be able to get a head start in the coming weeks to stay ahead of the curve.

![Peer Evaluation Term 2 Week 10](imgs/Madelyn%20DeGruchy%20T2%20Week%2010.png)

## Term 2 Week 9 (03/02/2026 - 03/08/2026)
- Dockerized our front-end so we are able to use the container for development
    - Container is live-mounted like backend so changes made copy straight to files on local machine
    - Used vite's dev server, in the container the system has trouble using the Hot Module Replacement (HMR). Currently I have added polling for the system to continually check for changes so that we are able to view the changes in the browser during development
- Added the static UI page to view the content of a resume, and set up how the user will be able to edit this content. This page is more to display what would be going on the resume so it is easy for the user to be able to edit it, we will need some further planning to structure how we want to display the resume in the format that they will be exporting it in.
    - Also added testing for this static page using Vitest
 
## Next Week
- Confirm which overall style to proceed with
- Begin implementing API calls between front-end and backend
- Decide on how we want to display the preview of the resume, and how we want to allow the user to export
    - We will also need to plan on how we will enforce a single page for this resume. 

## Reflection
 We had some confusion on which overall style we were going to move forward with. Once we have it nailed down we will be able to do some refactoring to ensure the whole system looks the same, but I think having some different options will help us plan how to best move forward.

![Peer Evaluation Term 2 Week 9](imgs/Madelyn%20DeGruchy%20T2%20Week%209.png)

## Term 2 Weeks 6 - 8 (02/09/2026 - 03/01/2026)
- Updated the flow of the prompts from the system to make the default response default to yes for everything except for LLM online consent and deletion (anything that was destructive or would allow for a security risk).
  - These defaults take place when the user enters an empty or invalid input, which allows the user to quickly go through the process when they are prompted to make decisions about their analysis. I added a default parameter to the config manager so that we can specify if we want the system to allow or deny consent.  
- Added missing testing for config manager, as well as for changes to default prompt flows
- Added the generation of resumes and portfolios to take place after the first run of analysis, and changed the menu to now have "Manage Resumes" and "Manage Portfolios" instead of the "Generate" option we used to have
  - When a user chooses to manage portfolios or resumes, they choose which analysis they want to view (given that both will be generated once analysis is complete, and the user can create multiple resumes and portfolios for each analysis), and then can choose which resume/portfolio they want to manage. From there, they can choose if they want to view, edit, delete, or generate a new resume.
  - Added deletion of resumes and portfolios to the database manager to support the deletion functionality.
  - Added the testing for all changes and new functionalities added from this work
- Created the API Documentation for all endpoints, including all possible responses
- Took part in all team meetings for planning the end of Milestone 2, took minutes for task assignments
- Collaborated on team slides for our presentation, and presented our Milestone 2 changes.
- Recorded the video for our Milestone 2 presentation for Sithara to record the voice over for

## Next Week
- We will be distributing tasks to be completed as we begin the implementation of our front-end at our meeting on Monday. The main tasks I have noted for completion are continuing to ensure we have decoupled the CLI from the flow of the system (though a lot of that work was completed by Devin this week), as well as looking into exactly how to set up and move forward with the React web app we are creating. We are fairly certain that the requirements for Milestone 3 will not change significantly moving forward, so we are planning to use those and our responses from peer testing as our structure to plan the next 4 weeks of implementation.

## Reflection
We have wrapped up Milestone 2 and are feeling optimistic about how it will translate to the creation of our front-end. Given that the final weeks of any term are full of many deadlines, we will need to ensure we are keeping on top of our weekly tasks to meet the tight turnaround of the next 4 weeks. As a team, we will need to make sure we have considered all of the tasks we will need to complete by the end of Milestone 3 so that we are able to schedule them accordingly. 

![Peer Evaluation Term 2 Weeks 6-8](imgs/Madelyn%20DeGruchy%20T2%20Week%208.png)

## Term 2 Weeks 4 & 5 (01/26/2026 - 02/08/2026)
- Changed how contributors in a GitHub project are counted
  -  The way that git logs (which the library PyDriller is built on) extracts the information about a given author varies from project to project and person to person. For example, I have one project where the author name is stored under my GitHub username for some of my commits, and under the full name attached to my GitHub account for others. The email attached to a commit also varies, and sometimes is my account email and sometimes is a privatized version that contains my GitHub username. Which version of both the username and email varies, and was also not consistent from project to project. While we were able to count the actual user accurately since they provide both their username and GitHub email, we needed better logic to count other contributors to the project without needing to explicitly tell the system the name, username, and emails of everyone the user ever collaborated with. We now map every instance to whichever username the system encounters first, and check for similar usernames or emails between all other commits.
  -  Also privatized the PII for these contributors to ensure no data is being stored unnecessarily
- Updated the logic for editing resumes to allow the user to edit the text that was previously generated instead of forcing them to always completley replace the section they want to edit
  - Also utilized helper methods to ensure that editing is consistent across all parts of the resume
  - Made date validation more robust
  - Added testing for this implementation and updated previous versions to support the new implementation
 
## Next Week
- Finalizing requirements for Milestone 2
- Complete the implementation of storage of the resume to the database
  - Slight refactor of how the user will access and edit this functionality, we want to generate a resume as soon as a new analysis is completed and allow a user to view all versions of a resume attached to an analysis
 
## Reflection
- Had some confusion on how we wanted to implement the storage of the resumes, will need to confirm with everyone the overall priorities of everything left to ensure that we are ready for Milestone 2

![Peer Evaluation Term 2 Weeks 4 & 5](imgs/Madelyn%20DeGruchy%20T2%20Week%204.png)

## Term 2 Week 3 (01/19/2026 - 01/25/2026)
- Implemented logic to allow the user to edit a resume that was generated
  - Given the ongoing database rework, this currently takes place immediately after the resume is generated given it could not be stored to be retreived later
  - Added the relevant testing for this editing function
- Assisted in troubleshooting the bugs from last week and diagnosing an issue where the number of contributors is miscounted.
- Participated in the weekly team meeting to plan tasks for the week

## In Progress
- I have started to change the logic used when considering stats for each author within a project to ensure that duplicates are counted properly

## Next Week
- Once all current PR's are merged, I will be able to store the generated resumes in the database so they can be viewed and edited at a later point in time. This PR will include logic to store and retrieve generated resumes, and will add options to the main menu to view previously generated resumes (all or by ID) and then allow users to edit these resumes that are retrieved.
- Have added a refactoring to update parts of the resume editing logic:
  - Move the add/remove logic that is similar to a helper method to clean up the current implementation
  - Allow the user to decide if they want to edit wording that is currently used for the summary, or start from scratch
- Finish the debug work to ensure contributors are counted correctly
  - Currently we can not identify the pattern of when the system uses the full name on GitHub vs when it uses the username that is attached to each commit. Given that depending on the users security settings, sometimes a commit has their personla email attached and sometimes it has the privatized GitHub noreply email. There also is not pattern between how these two fields (name and email) are connected. For example, I have a repository with some commits attached to (John Doe, JohnDoe@example.com) and other commits under (JohnDoe, 123456+johnsuser@noreply.github.com). In another repository, the same user was (johnsuser, 123456+johnsuser@noreply.github.com) and (John Doe, JohnDoe@example.com), and in another repository, these are flipped.
 
# Reflection
- Overall, made strong progress on another requirement, and just need to ensure the database is fully functioning to finish closing those 2.
- The team was able to resolve a lot of loose bugs and now has a strong understanding of where the others stem from. It will just take some time to fully implement the logic to get us closer to 99% accuracy

![Peer Evaluation Term 2 Week 1](imgs/Madelyn%20DeGruchy%20T2%20Week%203.png)

## Term 2 Week 2 (01/12/2026 - 01/18/2026)
- Completed the Resume Generation Implementation
  - Resume Data Processor collects the relevant data from each analysis pipeline (topic vectors, projects, and metadata) to be displayed in a resume
  - Resume Builder creates the Dict that stores each component under its own key. Once we implement the saving of the generated resume to the database, this will allow each component to be stored separately as well as the entire resume together. We plan to use JSON to store them.
  - Also updated main to add resume generation to the possible prompts for the user.
  - Added the testing for this new implementation
- Attended team meeting to plan to divide tasks
- Completed code reviews of teammates' code

# In Progress
- Still looking into the bug fix on contributions from last week. Although the fix I made worked locally (on Windows), Mac users continued to have issues. Since everyone was fairly busy this week, we have scheduled it to be worked on next week when I can sit down with Lexi and run some debugging on her computer

# Reflection
- It was a good week for making a dent in the requirements for Milestone 2. The current plan is to get all of the necessary requirements done as soon as possible and then spend the rest of this milestone refactoring and speeding up the processing time
- For next week, we are looking to get the major debug out of the way and then add the database implementation for the resume.

![Peer Evaluation Term 2 Week 1](imgs/Madelyn%20DeGruchy%20T2%20Week%202.png)

## Term 2 Week 1 (01/05/2026 - 01/11/2026)
- Worked on debugging for the timeline, not printing the names of the projects properly. Took me a while to determine where the issue was, but it ended up being an incorrect variable name in the display printing method and was not an issue in the actual extraction or anything
  - Added an additional test case to ensure timeline titles don't return as Unknown when a valid name for projects is included
- Took part in team meetings, given that everyone has new timetables, we were not able to meet until Wednesday so we had a shorter timeline to complete tasks
- Working on bug mentioned in my In Progress section

## In Progress
- I have been working on a bug raised by Sithara where certain projects are being picked up as Git repositories but contribution insights are returning as none/unknown and the project did not always appear in the timeline
  - I was able to replicate this on my computer with an old project where we only worked on a Development branch and have committed changes to ensure that our system now considers commits made in _all_ branches and not just what has been merged into main. Since I was unable to check this solution with her projects, I am holding off on opening the PR to merge this fix until we are able to do further troubleshooting to ensure this was actually the issue.
    - This debug was about 4 hours of diagnosing, while the fix was one line so hopefully that will be all that is needed.
   
## Reflection
- We had a bit of a later start, and I mainly spent my time diagnosing and debugging this week. Both fixes ended up only being 1-line, so both branches PR's are very short.
- For next week we are looking to get the ball rolling on getting all requirements done before we move in to refactoring and adding additional functionalities

![Peer Evaluation Term 2 Week 1](imgs/Madelyn%20DeGruchy%20T2%20Week%201.png)


## Week 14 (12/1/2025 - 12/07/2025)
- Assisted in the bug fix for the mac vs windows issue (Worked through diagnosing issue - 5 hours Monday, worked on a separate PR while Lexi completed troubleshooting and final fix - 6 hours Saturday)
- Implemented the display and storage of project insights to the database
- Added the user email to what is considered for user commits, resolving an ongoing bug in how the user identifies their personal commits in a repository
  - Includes the necessary testing for this fix
- Discussed with Lexi and Sithara to divide final tasks needed to ensure completion of Milestone 1
- Assisted in preparing and presenting Milestone 1
- Reviewed team mate PR's
- Participated in team meetings

### Reflection
The issue with how docker was accessing hidden .git folders on Mac ended up being a much larger undertaking than was initially expected, so having Lexi and access to macOS with her laptop was incredibly helpful! Once we got into Saturday, she took the reins to really try and research possible solutions and was instrumental in getting that final fix together while I was updating the database and main integration to include the project insights and display them properly. Also, a shoutout to Sithara, who came straight from work to join in on the bug fix Saturday afternoon and evening! 

![Peer Evaluation Week 14](imgs/Madelyn%20DeGruchy%20Week%2014.png)

## Week 13 (11/24/2025 - 11/30/2025)
- Updated the project analysis pipeline to separate the extraction data returned from the analysis data returned to allow for saving to their respective databases
  - Moved extraction to the processing pipeline to ensure analysis is exclusively related to that analysis, as the file was beginning to get quite large
  - Refactored the testing to move the extraction to the processing testing and added additional cases to improve coverage
- Implemented the combined preprocess module to handle the data flow of the code and text pre-processing pipelines
  - Included some minor logic fixes/updates and minor bug fixes in PII removal
- Participated in team meetings and discussions with team members to resolve bugs as they came up

### For Next Week
- Record the video presentation and further plan for Wednesday's in-class presentation
- Meet with macOS user to resolve the current no .git folder bug

### Reflection
- During the review process, a bug was encountered in the repository extraction, such that it is unable to find .git folders on macOS only. It would appear this bug has always existed on the system but my extraction code was only ever run by the windows users so it was not caught until now. The system can find the .git folder during initial processing to begin that pipeline, but then Repository Processing fails due to there being "no .git folder". I have been researching potential issues (--exclude flag has some weird bugs according to the known issues board for Docker, difference between how macOS and Windows handle hidden folders) but I have had trouble properly testing these fixes as a Windows user. I am planning to find a time at the start of the week to sit down with one of our Mac users to be able to run debugging on their system. 

![Peer Evaluation Week 13](imgs/Madelyn%20DeGruchy%20Week%2013.png)

## Week 11 & 12 (11/10/2025-11/23/2025)
- Completed the extraction of Git contribution metrics, and removed potential pieces that could include PII (commit messages)
  - Includes a refactor to move the analysis portion to a new file repository_analyzer.py
  - Added testing for Git Contribution extraction
- Implement method to create a timeline of all project repositories from the user
- Implement analysis to find the rank of a user in a project
  - Labels their contribution level, overall rank in the project by commits, and what percentile of contributors they are in
- Calculate code vs test ratio
  - Find overall # of code files, test files, lines of code, lines of tests, and percentages to compare files and lines of code vs tests. Also includes boolean to check if the user wrote any tests in a project
- Update analyze_repository.py to return the new insights from above
- Took part in team meetings

### In Progress
- Continuing to brainstorm how to deepen analysis and provide portfolio specific outputs

### For Next Week
- Rework input of GitHub id to consider both their account email and username, to ensure full coverage of the users commits

### Reflection
- Had some confusion on what is actually expected for Milestone 1 for the analysis and needed to meet with the team on Wednesday to restructure our approach.
- Overall this week was very busy and put a serious time crunch on the work I needed to complete. Some portions feel rushed and may need to be included in a refactor next week

![Peer Evaluation Week 11 & 12](imgs/Madelyn%20DeGruchy%20Week%2012.png)

## Week 10 (11/03/2025 - 11/09/2025)
- Resolved bug that was preventing system from properly reconstructing .git folders
  - Made changes to tree_processor.py to prevent files in .git folder from being dropped as invalid nodes
- Slight refactor of repository_processor.py to return List[Dict[str, Any]] instead of the JSON formatted version for consistency with other pipelines. Previous implementation was due to misunderstanding so reverted to the more basic version.
- Began implementation of extraction of key statistics from .git folder. Notes on PR indicate that this is not the final version, since I want to ensure we are covering all necessary statistics to meet Milestone 1 Requirements. Current implementation is very strong start and covers the majority of what needs to be considered.
- Implemented testing to ensure .git files are not dropped in error in the future
- Implemented testing to check the return from the Repository Processor
- Took part in code reviews for team mates work
- Took part in team meetings to discuss upcoming plans for this project to prepare for milestone 1

### In Progress / For Next Week
- Finalize commit statistics to be extracted (very quick)
- Complete implementation of the extraction of relevant package/framework information from these repositories.
  - Currently furthering my understanding of how we can access these stats directly from Git, or if the only way will be by parsing through import statements.
  - Once this is finalized, both these statistics + commit specific statistics will be forwarded to the data cache.
- Implement further testing to ensure values are being returned properly for these statistics, as well as testing the edge cases where certain statstics cannot be returned
- Implement testing for the package specific extractions.

### Reflection
- Locating the bug was the primary issue for this week, as it was critical to being able to further any of this implementation.
- Though I do think that the currently extracted information from the commits covers most if not all of what is needed for the milestone's. I do want to check in with the team in this coming week to ensure that we are all on the same page for what will be needed. This past week was very busy for everyone with lots of midterms before reading week, so we are planning to regroup and check in this coming week now that it is easier to align schedules.

![Peer Evaluation Week 10](imgs/Madelyn%20DeGruchy%20Week%2010.png)

## Week 9 (10/27/2025 - 11/02/2025)
- Assisted with research for PII removal libraries
- Researched PyDriller -> a library to allow for extraction of information within the .git folder.
  - Main point of research related to how to use this library on the already parsed data to maintain the principle of least privilege. This is the reason that the repository processor currently rebuilds the .git file structure of each .git file being considered.
- Implemented the Repository Processor
  - Considers the List[nodes] of the Git Repositories that have been found in the tree processor to rebuild the .git folder structure
  - Includes basic return for current 'extraction' that will change to include PyDriller commit_traverse()
  - Added all relevant testing for this implementation
- Participated in team meetings/discussions in regards to ongoing development decisions
 
### For Next Week
- There is currently a bug such that PyDriller cannot read the specific binary version being rebuilt in a way that allows for extraction. Though it appears all files are being recontsructed properly I have encountered issues when using the PyDriller Repository class. When implemeneted directly on the file it will work as expected so I am going to continue to work on this issue to ensure proper extraction.

![Peer Evaluation Response Week 9](imgs/Madelyn%20DeGruchy%20Week%209.png)

## Week 8 (10/20/2025 - 10/26/2025)
- Refactored _isCode() and _isText() to match the refactor of the attributes structure of file nodes in the file manager
- Added new helper method _getExtension() to retrieve the extension of the node passed from the tree processor
- Refactored testing of the file classifier for parity with file manager node attribute structure, including new MockNode() helper method
- Assisted in troubleshooting the validate-main-test branch, where a test directory and file could not be committed to the repo
- Took part in team discussions to determine tasks for the week
### For Next Week
- We will be meeting on Monday to set out next week's issues, and to plan some additional issues to be assigned to be prepared for the coming weeks
- Further research PyDriller to be prepared to begin the metadata analysis pipeline.

![Peer Evaluation Response Week 8](imgs/Madelyn%20DeGruchy%20Week%208.png)



## Week 7 (10/13/2025 - 10/19/2025)
- Implemented the helper methods isCode() and isText() for classifying files
- Collaborated on the file classifier
- Wrote testing for helper methods

### In Progress
- Working on refactoring the file classifier to consider the full node passed from the tree -> this changes current checks from strings to the full node
- Will need to fully refactor testing, current implementations are very string-specific

### For Next Week
- Discuss refactoring of tree processing as it changes how it passes a full node object instead of just the name (string)
- Add issues for the rest of Milestone 1, discuss further task assignments with the group

![Peer Evaluation Response Week 7](imgs/Madelyn%20Degruchy%20Week%207.png)


### Weekly Tasks Image

## Week 6 (10/06/2025 - 10/12/2025)
- Updated Requirements to reflect finalized Milestones and changes needed to the system.
- Performed code reviews for PR's in the project
- Participated in team meetings to discuss changes to architecture, DFD, and WBS
- Researched PyDriller, a library to be used to mine .git folders saved locally
- Updated README to include DFD and System Architecture with explanations provided by the rest of the team

![Peer Evaluation Response Week 6](imgs/Madelyn%20DeGruchy%20Week%206.png)

## Week 5 (09/29/2025 - 10/05/2025)
- Discussed DFD diagrams in team meetings
- Assisted in the creation of the level 0 and level 1 diagrams
- Helped create team logs

![Peer Evaluation Response Week 5](imgs/Madelyn%20DeGruchy%20Week%205.png)

## Week 4 (09/22/2025 - 09/28/2025)
- Worked with the team through the design process of the System Architecture Diagram in class
- Kept minutes through team meetings
- Coordinated the task dispersal of the Use Case and Requirement sections of the Project Plan
- Collaborated on the final Project Plan document
- Set up a branch for project-plan and converted the project plan file to markdown
- Received help from Sara on the proper use of images in markdown
- Contributed to team discussions on use cases and further implementation plans
![Peer Evaluation Response](imgs/Madelyn%20DeGruchy%20Week%204.png)
## Week 3 (09/15/2025 - 09/21/2025)
- Contributed to functional and non-functional requirements
- Completed final formatting for requirements documentation
- Took part in team discussions regarding initial project set-up and planning
<img width="1063" height="652" alt="image" src="https://github.com/user-attachments/assets/507c07f5-5739-408a-a234-71065c8395cf" />


