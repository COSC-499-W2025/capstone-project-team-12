# Features Proposal for Mining Digital Work Artifacts  

**Team Number: 12**  

Team Members:  

- Sithara Chari 22066401
- Devin Huang 86828886
- Lexi Loudiadis 93546844
- Sara Srinivasan 10801751
- An Tran 79499364
- Madelyn DeGruchy 85064962

## Project Scope and Usage Scenario

This system will allow graduating students, or other professionals who regularly use a computer for their work, to be able to track their personal progress as well as generate meaningful insights to be used in a portfolio or resume. These users will be able to upload files in a safe manner that will ensure any personally identifiable information has been removed. The system will then create a dashboard for the user to help detail insights from their work, including languages, frameworks, and libraries they’ve used, as well as resume-oriented breakdowns of previous projects.

## Proposed Solution

Our solution is an intelligent app that extracts a bag of words from user-provided files, code repositories, and documents (with PII removed) and passes this data to an ML model to generate topic vectors that are processed by a Natural Language Generator to output resume-relevant skills while simultaneously producing analytical graphs and metadata visualizations. Unlike other teams, we will be using advanced NLP models like pyLDavis to analyze the users’ works and extract skills and qualifications that the user might otherwise overlook.  

## Use Cases  

![UseCaseUML](imgs/UseCaseUML.jpg)

Use Case 1: Generating Insights

- Primary actor: Graduate students or early professionals  
- Description: A user wishes to generate insights based on the files they uploaded. They click on the “Generate Insights” button, and sit back as the software generates a custom resume-ready portfolio for them.  
- Precondition:  
  - The user has uploaded all relevant files and preprocessing/classification has been completed  
  - The Bag of Words was successfully created and is ready for analysis by the NLP model  
- Postcondition:  
  - The system generates a text summary highlighting relevant skills and contributions in a resume-ready format  
  - These results are displayed to the user in an HTML page

Main Scenario:  

1. The user has already uploaded their files and is ready to see the results  
2. The user clicks the “Generate Insights” button.  
3. The system reviews the files and identifies patterns, topics, and skills  
4. The system renders the findings into insights about the user’s work  
5. The insights are prepared in a simple format that can be added to the user’s portfolio or resume  
6. The user views the insights in their web browser

- Extensions:  
  - 2a. No useful information is found: If the uploaded files do not contain enough useful content, the system tells the user that no insights could be generated.  
  - 3a. Insights unclear: If the system cannot recognize specific patterns in the data, it provides a more general output instead  
  - 4a. Display issue: if the insights cannot be shown in the normal resume-ready format, the system will show them to the user as plain text instead

Use Case 2:  A graduate student or early professional uploads their notes,papers and other academic text file.  

- Primary actor: Graduate students or early professionals  
- Description: The user wants to upload their notes, files and other academic data, so the system can analyze it and extract relevant skills and contributions, creating a summary that is ready to put on a resume.  
- Precondition:  
  - The user must have access to the web application  
  - The user has notes, codebases, papers and other academic text data in accepted formats. (txt, md, pdf, most code extensions, etc.)  
- Postcondition:  
  - The system generates a text summary highlighting relevant skills and contributions in a resume-ready format

Main Scenario:  

1. The user clicks the “upload” button.  
2. The user browses through their files and selects the research paper files  
3. The system validates the file format and content  
4. The system analyzes the paper  
5. The system generates a text summary that is resume-ready  
6. The user views the summary and has the option to save it

Extensions:  
2a. Invalid file format: The system notifies the user that invalid data was entered and repopulates the form with the data that the user previously tried to enter.  
4a. If the analysis fails (unreadable file), the system notifies the user of which file was unreadable and returns the user to the ‘upload files’ page

Use case 3: An individual clears uploaded files

- Primary actor: Graduate students or early professionals  
- Description: The user wants to remove previously uploaded files from the system.  
- Precondition:  
  - The user has access to the web application  
  - At least one file has already been uploaded  
- Postcondition:  
  - The selected files are removed from the system and no longer available for insight/analysis

Main Scenario:

1. The user navigates to the timeline section  
2. The user selects one or more files that they wish to remove from the system  
3. The user clicks on the “Delete selected file” button  
4. The system shows a popup asking for confirmation before deletion  
5. The user confirms the action  
6. The system removes the selected files  
7. The system updates the timeline to reflect the change

Extensions:  
2a. No files available: If no files were uploaded before, the system displays a message “No files to clear”  
4a. The user cancels: If the user cancels at the confirmation prompt, no files are deleted and the system stays in the current state.

Use case 4: An individual browses the timeline of previously generated insights

- Primary actor: Graduate students or early professionals  
- Description: The process of browsing the timeline of previously generated insights.  
- Precondition: The user must have access to the web app and have generated an insight previously.  
- Postcondition: The user can see the chronological timeline of previously generated insights.

Main Scenario:  

1. The user clicks on the “Timeline” button  
2. The system displays the timeline, divided by month, and each generated insight is represented by dots on the timeline  
3. The user can scroll through the timeline and hover over the dots to see additional details

Extensions:  
2a. If there is no previously generated dashboard, the system will display “No insights generated yet.” and the timeline will be empty

Use case 5: An individual views a previously generated dashboard

- Primary actor: Graduate students or early professionals  
- Description: The process of viewing a specific dashboard.  
- Precondition: The user must have access to the web app and have generated a dashboard previously.  
- Postcondition: The user can view full details of a specific previously generated dashboard

Main Scenario:  

1. User clicks on the “Timeline” button  
2. The system displays the timeline, divided by month, and each generated insight is represented by dots on the timeline  
3. User clicks on one of the dots on the timeline  
4. The system displays the selected dashboard

Extensions:  
2a. If there is no previously generated dashboard, the system will display “No dashboards generated yet.” and the timeline will be empty

Use case 6: An individual clears previously generated insights

- Primary actor: Graduate students or early professionals  
- Description: The process of removing an individual, some or all of the previously generated results from the system.  
- Precondition: The user must have previously uploaded file(s) and generated insights. The system needs to have successfully saved these results once they were generated.  
- Postcondition: All previous insights selected for deletion are removed from the database and they no longer appear on the timeline.

Main Scenario:

1. User clicks on the "Clear Previous Insights" button from the timeline or on the dashboard for the individual insight  
2. The User then selects the insights (grouped by the root directory selected by user for analysis) or can select to "Clear All"  
3. The user submits their selections  
4. The system shows a pop-up confirming the selected insights for removal  
5. The user confirms the action  
6. The system will remove the generated artifacts and insights from the database  
7. The system will update the timeline to remove the artifacts and insights  
8. The system notifies the user about the successful removal of the data

Extensions:  
1a. No insights available for export: The user will not be able to access the button to  
5a. The user cancels: if the user decides not to remove the insights they have selected when the system prompts them to confirm, then the system will not remove any data from the database

Use case 7: An individual exports generated insights

- Primary actor: Graduate students or early professionals  
- Description: The process of exporting the generated insights for use in resumes or a portfolio.  
- Precondition: The user must have uploaded file(s) and successfully generated insights.  
- Postcondition: The selected insights are exported in the requested format and saved to the user's specified location.

Main Scenario:

1. User clicks on the "Export Results" button, visible when viewing a specific generated insight  
2. User chooses the export format (CSV, DOCX, PDF)  
3. User specifies the name and location for the exported file  
4. The system formats the results as specified by the user, generates the export file and saves it to the specified location.  
5. The system notifies the user that the file was exported and saved successfully

Extensions:  
4a. File already exists at the location specified: System warns the user that a file of the same name already exists at that location and allows them to change the name, cancel the export, or replace the previous file  
2a/3a: The user cancels the export: If the user decides to cancel, then the system will not generate any export files

4.**Requirements, Testing, Requirement Verification**  

- Front-end:  
  - React, JavaScript, Jest (testing)  
- Back-end:  
  - Python and PyTest (testing)  
  - Packages: nltk \- for stemming and lemmatization, spacy \- for lemmatization, Pygments for code/variable extraction and processing, pyLDAvis \- LDA-driven ML-NLP model for topic analysis, pyClustering \- for clustering exported topic data from NLP, pyLDAvis.gensim \- for visualizations in html, pickle \- for html export to front end

| Functional Requirement  | Description  | Test Cases  | Who  | H/M/Ea |
| :---- | :---- | :---- | :---- | ----- |
| Generate Insights | The system shall generate insights, such as skills, topics, and contributions, from uploaded files The system shall produce a topic vector from the preprocessed text data The system shall transform the topic vector into readable insights The system shall notify the user if no insights can be generated from the uploaded files The system shall display the insights to the user in an HTML format  | Test Case 1: Skills Extraction Input (topic vector): {python: 0.8, java: 0.6, sql: 0.4 Expected Output: \[“Python”, “Java”, “SQL”\] Assertion: Generated list equals expected skills Test Case 2: Synonym Matching Input: {js: 0.7, JavaScript: 0.5} Expected Output: \[“JavaScript”\] Assertion: Length of insights list \= 1; contains “JavaScript” Test Case 3: Empty Vector Input: {} Expected Output: “No insights available” message Test Case 4: Invalid Topic Vector Input: Topic vector with missing or corrupted values Expected output: Graceful error handling Assertion: No crash; error message displayed | Maddy, Devin, Sara Srinivasan - (Sithara, An, Lexi for Pre- processing) | Medium |
| Browse timeline | The system shall allow users to browse the timeline of previously generated insights. The timeline shall be sorted in chronological order and divided by month. Each generated insight shall be represented as an interactive dot on the timeline, and the user can hover over it to see basic information (time created, summary, number of files uploaded) or click on it to view the dashboard in full detail. The system shall display a button that allows the user to remove insights. If the user has not generated any insights, the timeline shall be empty and the system shall display the text “No insights generated yet.” | Test case 1: Multiple insights have already been generated → see insight dots on timeline Test case 2: No insight has been generated → empty timeline Test case 3: Insight dot being clicked on → navigate to view dashboard page Test case 4: Insight dot being hovered on → display info Test case 5: Not hovering on insight dot → make info disappear Test case 6: Cleared insight → not be displayed on the timeline | An, Sithara, Lexi | Medium |
| View Dashboard | The system shall allow users to view the dashboard. The dashboard may contain pie charts and graphs that allow the user to see relevant topics and skills gathered from the uploaded files of that insight. The system shall display a button that will let the user export the dashboard. The system shall display a button for the user to navigate back to the timeline. | Test case 1: Navigate back to timeline Test case 2: Relevant info (graphs, summaries) is displayed in the dashboard Test case 3: If a dashboard was deleted in another tab, any tabs with that dashboard opened shall display an error notification (async) | An, Sithara, Lexi | Medium |
| Upload files | The system shall allow users to upload files of supported formats. through the web interface. Uploaded files must be validated for type, size and also integrity before being processed. Complexity will arise from handling large files of different types consistently. | Test Case 1: Single supported file upload Test Case 2: Multiple file upload of the same format Test Case 3: Multiple file upload of various types Test Case 4: Unsupported file type rejection Test Case 5: File size limit enforced (too big) Test case 6: Integrity check failure (corrupted file) Test case 7: Uploading files of unsupported types.  | Devin, Sara, Maddy | Easy |
| Clear Uploaded files | The system shall allow users to clear previously uploaded files from the system. The removal must delete the file and all associated artifacts. The timeline browser must reflect this deletion consistently. Complexity will arise from deleting certain files with many associated artifacts. | Test case 1: Delete a single file from the system Test Case 2: Delete multiple files from the system Test Case 3: Check if a confirmation prompt appears before removal of files Test Case 4: Check if associated artifacts are also removed with the selected files Test case 5: No files to delete | Devin, Sara, Maddy | Medium |
| Export results | The system shall export results in CSV, DOCX, and PDF formats with proper formatting. This will involve implementing a format converter, templates to organize insights within the artifact, and handling different data types across these formats. Complexity will come from exporting certain types of insights across files, such as how to handle graphs in CSV vs PDF.  | Test Case 1: Export as PDF  Test Case 2: Export as CSV Test Case 3: Export as DOCX Test Case 4: Export to a location where a file with the same name and file type already exists Test Case 5: Export to a location where a file with the same name and a different file type already exists Test Case 6: Export to an invalid location Test Case 7: User cancels the process before it is completed | An, Sithara, Lexi | Medium |
| Clear previous insights | The system shall allow the user to remove the insights that were previously generated. This includes the ability to view a list of all insights generated to select 1 or multiple to clear, as well as a “clear all” option for the user to be able to start fresh. This will involve connecting with the database to allow for deletion and adequate user warnings to minimize accidental deletion. Potential difficulties may arise if the user is deleting a large amount of files simultaneously and how long the system will take to process that. | Test Case 1: Remove a single insight Test Case 2: Remove Multiple, but not all insights Test Case 3: Remove all insights Test Case 4: No insights available for removal Test Case 5: User cancels during the process | Sara, Maddy, Devin | Easy |

---

| Non-functional Requirement | Description |
| :---- | :---- |
| Processing capacity and speed | The system shall process through 5GB of files within 120 seconds |
| RAM usage under normal use conditions | The system shall operate within 500mb of RAM under normal use conditions |
| RAM usage under peak conditions | The system shall use no more than 2GB of RAM under peak conditions |
| Categorization accuracy | The system shall categorize files with 98% accuracy |
