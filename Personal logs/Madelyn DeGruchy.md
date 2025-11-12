# Madelyn DeGruchy Personal Log (85064962 - maddydeg)
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


