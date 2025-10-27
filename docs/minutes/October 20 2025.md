# October 20th Meeting

## General Notes
### Tree Node 
Attributes to include:
- Name:
- Type: (to be done in file classifier)
	- Possible Types file, and directory
- Extension:
- Size: 
- Pointer: (to binary)

Type to be set in the classifier, the rest are initialized in the manager. Next week will look into custom new node structure.

## To Do This Week:
- Refactor the File Classifier and testing
   - Dismiss files that have the 'other' classification
- Continue Code Preprocessor
- Complete Dockerization & get database to persist 
 - Move testing in to the corresponding folder -> backend testing in the backend folder etc.
- Implement PyTest testing for File Manager
- Update App.py to run tests
- Clear output function to pass to preprocessors
	- getTextFiles() and getCodeFiles() return an array of files [name, extension, index, binary]
	- getGitDirectories() return a set of sub trees


## Assignments
- Sara: Complete Dockerization
	- Sara: Set up test directory in testing refactor
- Sara: Implement Code Preprocessor and write testing
- Sithara: add type attribute (empty) to node and ensure .git folders are being properly identified (includes writing more tests). Also refactor to add pointer to binary rather than storing the file manager.
- Devin, An and Maddy: Update tree processor implementation
  - Update the file classifier to consider the nodes specifically (manager parody).
  - Include output functions as specified above. 
- Lexi and Sithara: Update the main.py/app.py with defined methods and to run testing (Lexi talk to Sithara to better understand what this entails)

## For Next Week
- Tree rework
	- Tree helper functions (getSize(), getExtension(), isFolder(), isFile(), other functions to access fields. TreeImplementation.py to store node definition, and include all the helper functions) Make a new node implementation in this file for file manager to call. Use this instead of anytree's new node
	- custom tree class in TreeImplementation.py -> custom new node to create a node with all empty attributes needed
