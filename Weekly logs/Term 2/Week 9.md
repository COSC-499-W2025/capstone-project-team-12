# Week 14 (01/05/2025 - 01/11/2025)

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

- Refactored analysis pipeline to remove dependency on the CLI.
- Added callbacks to primary analysis pipeline
- Updated testing to match modified architecture

Frontend updates:

- Decided on designs for remaining core frontend pages
- Updated frontend to be dockerized instead of host-system based.
  - src code is live mounted and a polled vite dev server is deployed for live updates and rapid development
- Implemented sidebar component and initial onboarding page
- Implemented the Project Insights UI (PR #460)
- Testing for the Project Inishgts UI: 12 tests, all passing (PR #467)
- Added Initial resume page, pending UI Design for user interaction.
- Designed and implemented static progress page.

### Burnup chart & Task Table

![T2 Week 9 Burn Up](/imgs/T2%20Week%209%20Burnup%20Chart.png)

![T2 Week 9 Tasks Table](/imgs/T2%20Week%209%20Task%20Table.png)
Filtered to only show Tasks with changes this week.

### Test Report

![ T2 Week 9 Test Report Frontend](/imgs/T2%20Week%209%20Frontend%20Test%20Report.png)
![ T2 Week 9 Test Report Backend](/imgs/T2%20Week%209%20Backend%20Test%20Report.png)

### In Progress

- Completion of deduplication to track file hashes in session and in db for efficiency
- E2E Api Tests

### Upcoming plans

- Finish up design and static implementation for all core pages
- Begin implemention of front-end logic and front end to backend api calls
- Address style inconsistencies between pages(current and future)

### Reflections

- Good start for Milestone 3. Core design, tech stack and deployment are in place. Reasonable progress on static UI pages
- E2E tests still in backlog, needs to done by end of next week at the latest.
