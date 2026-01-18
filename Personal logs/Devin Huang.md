## Devin Huang Personal Log (86828886)

[Term 2 Week 2](#t2-week-2)  
[Term 2 Week 1](#t2-week-1)  
[Week 14](#week-14)  
[Week 13](#week-13)  
[Week 12](#week-12)  
[Week 10](#week-10)  
[Week 9](#week-9)  
[Week 8](#week-8)  
[Week 7](#week-7)  
[Week 6](#week-6)  
[Week 5](#week-5)  
[Week 4](#week-4)  
[Week 3](#week-3)


### T2 Week 2
- Implemented user validation for extracted topic keywords (https://github.com/COSC-499-W2025/capstone-project-team-12/pull/310)
  - Give the user control over the keywords sent for summary generation (Replace, change, delete, add)
- Implemented user skill highlight selection (https://github.com/COSC-499-W2025/capstone-project-team-12/pull/316)
  - Select up to 3 skills + ability to add custom skills to highlight in summary
- Team meeting
- Implemented testing for all related tasks
#### Next week
- Reword the database manager module
- Change Ollama specification to be a specific version instead of latest version

#### Reflection
- This weeks work was rather straightforward, everything was quite easy to implement due to the refactoring that we did last week.

<img width="960" height="485" alt="image" src="https://github.com/user-attachments/assets/5ed7b4fe-5657-4136-a5c8-916658e657c7" />


### T2 Week 1
- Refactored main by extracting the analysis pipeline logic and all the CLI related logic into individual classes
- Added testing for the newly created `analysis_pipeline.py`
  - Comfirms that the pipeline handles binary correctly
  - Comfirms that it handles file reading errors
  - Simulates successful analysis run
- Team meeting
#### Next week
- Refactor the LLM clients
- Work towards the milestone 2 requirements completion

#### Reflection
- We had our team meeting later than usual, which kind of made things rushed, therefore we didn't start on any big term 2 requirements yet.
- This weeks refactoring highlighted how bloated our main.py file was. We were able to decrease the length of it from 500+ lines to around 100.

<img width="962" height="491" alt="image" src="https://github.com/user-attachments/assets/27d80b8f-dfe0-4590-b27a-0e27921a45f2" />



## TERM 2

### Week 14
- Resolved an issue where mac users could not run the local llm due to docker memory limitation
  - Apparently Docker desktop on MAC does not reserve memory dynamically, unlike on windows. Raising that limit fixed the issue.
- Optimized the prompt for the medium length local LLM summary
- recorded milestone 1 demo video
- Participated in team presentation
### Next week (break)
- Bug hunt
### Reflection
- This week has been rough, I was sick in the beginning and had exams spread accross this week, and two finals on monday and tuesday. I do realize that I have not done enough coding wise, but I believe that I needed to focus on my exams.
<img width="802" height="568" alt="image" src="https://github.com/user-attachments/assets/073b2feb-6244-4368-ba87-0784bc6b4447" />

### Week 13
#### This week
- Implemented the local llm and online llm into the main pipeline (https://github.com/COSC-499-W2025/capstone-project-team-12/pull/195)
- Implemented the stats and data cache into main pipeline 
- Implemented the database manager module:
  - Added saving, reading and removing databbase functions for various elements
  - Created tests for the database module (https://github.com/COSC-499-W2025/capstone-project-team-12/pull/216)
- Refactored various modules so that only the topic vectors are passed into the llm client instead of whole bundle (https://github.com/COSC-499-W2025/capstone-project-team-12/pull/232)
- With the help of Sithara and Sara, found and fixed multiple bugs with the pipeline.
- Fixed an issue with the response time with the local llm.
  - Updated `main.py`, `topic_vectors.py` and both llm modules (mostly prompt changes)

### Next week
- Record video presentation for milestone 1
- More refactoring and adding guardrails for the llm client prompts

### Reflection
- The main issue this week was the lack of time to implement and make sure all componenets work together, it was a pretty busy week for me
- A lot of small issues arised trying to put everything together

<img width="958" height="487" alt="image" src="https://github.com/user-attachments/assets/e30a86b1-f406-4559-81a7-f4def8505b7f" />

### Week 12
#### This week 
- Implemented the local llm and containerized it into docker (https://github.com/COSC-499-W2025/capstone-project-team-12/issues/143)
  - Docker:
    - Added local-llm.dockerfile for an Ollama Phi-3 Mini container
    - Updated docker-compose with a local_llm service, memory limits, and a persistent volume
    - Added health checks and test port
  - Backend:
    - Backend now depends on the local_llm service
    - Renamed llm_api.py to llm_online.py and refactored LLMAPIClient to OnlineLLMClient to make it more clear
    - Added llm_local.py with LocalLLMClient for Ollama
    - The current prompts are still not optimal for the smaller model, but these will be changed later on, as they are not major issues.
    - Added short, standard, and long summary methods (120-second timeout, although with bigger bundles, we might need more time)
- Wrote tests for the local implementation of the llm: (https://github.com/COSC-499-W2025/capstone-project-team-12/issues/179)
  - Updated test_llm_online.py with new names and made sure that all tests pass
  - Added test_llm_local.py
#### Next week
- Add the newly implemented local llm and online llm into the main pipeline for the insight generator
- Fix any bugs related to the pipelining and integration of these modules into `main.py`

#### Reflection
- The main factor that slowed me down this week was all the documentation that I needed to read before actually implementing the local llm and how to make it function with docker.

<img width="1201" height="617" alt="image" src="https://github.com/user-attachments/assets/726ff967-d37f-464b-ae2b-f7ed7111df4b" />


### Week 10
#### This week
- Implemented a basic version of the statistics and data cache (https://github.com/COSC-499-W2025/capstone-project-team-12/pull/136)
  - Currently supports any type of dict formatted data since previous components are not fully implemented.
  - This module bundles the results of the metadata analysis, project analysis and text analysis together to make it easier later to process all of this in later components
  - It serializes structures that aren't supported by JSON (converts sets, tuples, and frozensets to lists)
  - Handles nested data structures recursively to ensure deep conversion
  - Includes error handling for serialization failures and unexpected errors
  - Returns formatted, alphabetically-sorted JSON strings ready for database storage
- Wrote testing for the statistics and data cache (https://github.com/COSC-499-W2025/capstone-project-team-12/pull/136)
- Wrote testing for the error handling for tree_processor.py (https://github.com/COSC-499-W2025/capstone-project-team-12/pull/122)
- Collaborated with team members on integration

#### Next week
- Finalize the statistics and data cache wiht stricker error hanlding once the other componenets have been fully implemented
- Add more testing as this module gets more and more complete
- Start looking at how to implement the insight generator
- Make the statistic and data cache actually save the bundle to database

#### Reflection
- The main issue I had this week for the implementation of the statistic and data cache was that teh previous components were not fully implemented yet, making it difficult to know exactly what was going to be inputed as arguments.
  - To address this, I implemented a flexible, generic design that accepts any dictionary structure.

<img width="956" height="495" alt="image" src="https://github.com/user-attachments/assets/47209ef8-4509-4dd9-9d4f-6d454b513f58" />

### Week 9
#### This week
- refactored tree_processor.py so that the getter functions return the nodes themselves instead of the file paths in the arrays
- Added error handling for 'main.py' and 'tree_processor,py'
  - Implemented safe key access, try-except blocks for processing and classification, and node traversal resilience
  - Added handling of KeyboardInterrupt and unexpected exceptions for clean exits
  - Made sure that previous tests remained passing
 - Participated in team meetings
#### Next week
- Add more edge testing in regards of newly implemented error handling
- Start researching and potentially working on text analysis component (transform bow into topic vectors)

<img width="968" height="495" alt="image" src="https://github.com/user-attachments/assets/ddb75aef-624d-4445-9ca4-a137cf166168" />


### Week 8
- Refactored tree_processor from function-based to class-based implementation
- Updated tests to reflect the change in the tree_processor file
- Added getter methods to TreeProcessor: get_text_files(), get_code_files(), get_git_repos() to return file path arrays
- Updated main.py to correctly instantiate TreeProcessor class instead of calling as function
- Helped teammate running tests in the docker container
- Contributed in team discussions talking about weekly tasks
#### Next week
- Plan a meeting to discuss the separation of tasks (might also change meeting dates so that it fits better with the checkin dates)


<img width="964" height="504" alt="image" src="https://github.com/user-attachments/assets/320b78c1-5fd4-4191-990e-f31390bf7af5" />


### Week 7
- Implemented tree processor component for file classification system alongside it's tests, which all passed
- Updated tree processor component to import correctly the other members work (from file_classifier import getFileType)
- Set up pytest testing framework in Docker environment
- Added a .gitignore file to exclude Python cache and test cache
- Participated in team meetings regarding task priority and assignment

<img width="1174" height="603" alt="image" src="https://github.com/user-attachments/assets/59ec3b7a-8395-44e6-9f7e-1f387dd42000" />

### Week 6
- Created the documentation for the WBD
- Created the diagram for the WBD
- Contributed to requirement table review
- Participated in group meetings and discussions about updated architecture and task grouping

<img width="1067" height="622" alt="image" src="https://github.com/user-attachments/assets/5c4c3246-5696-43a0-af7c-68599f66c189" />


### Week 5
- Contributed in the creation of the level 0 and 1 of the data flow diagram
- Participated in discussions regarding ours and other teams DFD to enhance and refine our own diagram
- Did research on PylDavid NLP model in topic modelling for later implementation purposes

<img width="1083" height="635" alt="image" src="https://github.com/user-attachments/assets/67bc560b-ba19-4757-baf4-8fe9cba5ee4d" />

### Week 4
- Participated and contributed to discussions regarding the updated architecture  
- Contributed to writing documentation for the project proposal  
- Helped specify requirements and use case scenarios

<img width="1074" height="542" alt="image" src="https://github.com/user-attachments/assets/c86b1365-289d-4c10-8ac1-b36dfb24e5fb" />

### Week 3
- Contributed to creating the functional and non-functional requiremnents
- Took part in cross-team discussion to find missing requirements

<img width="1075" height="631" alt="image" src="https://github.com/user-attachments/assets/b33b2f49-de35-4c00-9b39-346294c60094" />


