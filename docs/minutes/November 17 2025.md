# November 17, 2025
## This Week
- Rework prompting in main to ensure everything is integrated -> Sithara
- Integrating local LLM and online LLM -> Devin
  - Once complete, we will be able to help with main
- Metadata analysis -> An
- Project deeper analysis and framework/language extraction -> Maddy (finish basics for Wednesday to ensure we can split tasks with Lexi)
- Assist in the deeper analysis of the project analysis pipeline -> Lexi
- Database helper functions -> Sara

## Notes
- Will have MVP by the end of next week
- Use a class object to be able to use JSON to save to database
- All 3 pipelines will send back to main, main will call components to get the return value and then main will call database to save them all together
  - For retrieval, will rework user input
- Final output will essentially be a wall of text, no HTML or anything for Milestone 1
- Next week will be about cohesiveness rather than adding any new features
- How many parameters for a local model?
  - 2 - 4 billion (ish) parameter range, could give it a more robust input to increase the overall quality
  - Aim for 2 - 3 GB of RAM, and 2 - 3 minutes. 
