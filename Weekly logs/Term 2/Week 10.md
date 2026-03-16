# Week 10 (03/09/2026 - 03/15/2026)

## Team 12

### Team Members

| Name             | GitHub Username |
|------------------|-----------------|
| Sithara Chari    | sitharachari    |
| Madelyn DeGruchy | maddydeg        |
| Devin Huang      | devin201o       |
| Lexi Loudiadis   | lexilouds       |
| Sara Srinivasan  | Eveline36       |
| An Tran          | antran-17       |

### Work Done

Backend updates:
- Finished E2E-Testing for the API PR #[#494]
- Added new endpoints for app-level config management (set/edit/retrieve arbitrary config values) to support frontend state 
- Updated backend to support storing user-populated fields (awards, education, and previous work experience) for the resume PR #486 
- Completed the refactor of the file deduplication feature pr #471  
- Implemented the first half of the dashboard API endpoint connections (mapping analyses, delete endpoints). PR #492 

Frontend updates:
- Implemented the UI for the dashboard page (create new analysis, add files, delete analyses, view portfolios/resumes/skills) PR #475 & PR #478 
- Created the file upload page supporting single/batch file and folder uploads, removal, and auto-zipping PR #473
- Finished coding and testing the fine-tuning page PR #497 and #500
- Updated the resume page to make API calls, allowing users to view, edit, and save changes to the database PR #486
- Implemented state persistence for the onboarding and upload pages (GitHub username and email persist through tab changes) PR #482
- Connected the onboarding and upload pages to the actual API (sends config and zipped files to extract endpoint) #482
- Switched the portfolio UI to "light mode" to resolve team design inconsistencies #478

### Burnup chart & Task Table


![T2 Week 10 Tasks Table](/imgs/T2%20Week%2010%20Task%20Table.png)
![T2 Week 10 burnup chart](/imgs/T2%20Week%2010%20Burnup%20Chart.png)



### Test Report

![week 10 frontend test](</imgs/T2%20Week%2010%20Frontend%20Tests.png>)

![week 10 backend test](</imgs/T2%20Week%2010%20Backend%20Tests.png>)

### In Progress

- Continuing to hook up dashboard API calls and connect remaining frontend pages to the backend.
- Reworking the progress page to match the rest of the app's light theme.
- Integrating the analysis pipeline process with the loading screen to provide better visual cues to the user.

### Upcoming plans

- Finalize the routing strategy (e.g., how the `resumeId` is passed and handled without the sidebar).
- Implement the heatmap feature for the dashboard.
- Link all remaining static pages to the backend API to create a seamless user experience.
- Polish UI consistency and ensure the basic flow of the system is fully intact in preparation for Peer Testing #2 next week.

### Reflections

- The team had a highly productive week focusing heavily on frontend-backend integration. By adding features like app-level config management on the backend, we were able to significantly speed up frontend development.
- Despite busy schedules and some personal hurdles over the past few weeks, the team has communicated effectively and adapted well. We are feeling very optimistic about having a polished final product ready for the Milestone 3 presentation and demo, and a good UI for peer testing. 