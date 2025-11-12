## Devin Huang Personal Log (86828886)

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


