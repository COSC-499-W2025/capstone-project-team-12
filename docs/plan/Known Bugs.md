# Capstone Known Bugs and Future Suggestions

### Known Bugs
- Failed to load analysis toast when there are none done.
- If a user does go back to finetuning from a later step using the sidebar, they will receive a toast that says “Error processing data. Please check console” and an error in the console for cache expired or no valid analysis id. The only way for the user to proceed is using the sidebar. 
- When a user manually edits the number of lines in a project for a portfolio, some of the metrics do not get recalculated automatically. 

### Future Suggestions:
- Block certain steps in pipeline when we are at certain numbers (Shouldn’t be able to go back to onboarding and file upload when we are at finetuning). Could just make the previous/later phases unclickable or greyed out.
- Include project stats in data sent to the LLM to add further context to generated summarys 
- If a project’s end date is towards the end of the month, the starting labels of the heatmap will overlap as the column space the first month requires is less than the length of the label itself 
- Align the Progress Page with the specific steps that it is currently working through. 
- Add the front end functionality for uploading thumbnails to an analysis and displaying them on the dashboard.
- Add the front end functionality for regenerating a resume or portfolio and allowing a user to generate multiple resumes and portfolios for each analysis
- Allowing the user to share the public version of a portfolio. Currently we visually support a public and private mode, but they can only be viewed by the user in their current form. 
