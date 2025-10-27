# October 27 Meeting Minutes
## Notes
- Sara has invited everyone to the testing subrepo
  - Has no protection, can add whatever you want, but do not remove/rename anything
- New team processes
  - Have PR's completed by Thursday afternoon (by 3 pm)
  - Merges to be completed by Saturday noon
  - Sunday is reserved strictly for logs
- For File Manager Array
  - Create in the file manager and pass to main.
  - Main will store it, and everyone who needs to access this array will import it from main
  - Main will continue to pass the tree to the tree processor to return the 3 arrays (code files, text files, and git repos)

## To Do This Week
- Wrap up your current components
  - Any debugging, additional testing,    
- Refactor of spacy to use Gensim (Sara)
- Include return types and declaration types
  - ex: include from anytree import node
  - ex: def method (node: node) -> returnType
- Preference for inline comments
- PII Removal

## Assignments
- Gensim refactor -> Sara
- Code Processor Testing -> Sara
- Text Processor refactor (as part of Gensim) -> Sara
- File Manager refactor to change how binary data is saved (in array) -> Sithara
  - Will now return the tree and the array, and only pass the array to files that need it
  - Add return types and variable types
- PII Removal (Lexi and Maddy)
- Return types, expected type, declared types and error handling on all current classes (Devin and An)

## For Next Week
- Begin Analysis planning
- Start the MetaData pipeline
