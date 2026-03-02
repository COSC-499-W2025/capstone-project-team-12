# Term 2 Weeks 6 - 8 (02/09/2026 - 03/01/2026)
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
* Implemented portfolio result and skills endpoints (PR #394)

  * Implemented `GET /portfolio/{result_id}` using PortfolioBuilder
  * Implemented `GET /skills` with proper aggregation across analyzed projects
  * Added associated interface/implementation tests
  * Updated `docker-compose.yaml` to run Uvicorn for local API access

* Implemented incremental update API endpoint (PR #435)

  * Split pipeline into extract and commit endpoints for user-interactive updates
  * Extract endpoint merges new data and returns raw metrics
  * Commit endpoint trusts frontend ranking, generates LLM summary, and saves state
  * Set up OpenRouter API key

* Refactored upload endpoint architecture (PR #440)

  * Fully decoupled upload from CLI and fixed EOF crash
  * Split upload into extract and commit-style endpoints
  * Updated tests and removed obsolete ones

* Reworked main pipeline output for Milestone 2 (PR #436)

  * Improved wording for prompts, errors, and info displays
  * Removed database query info from output
  * Fixed KeyboardInterrupt (Ctrl+C) issue
  * Formatting improvements

* Added online LLM API key setup instructions to README (PR #436)

* Portfolio UI implementation and tests (PR #426, #427)

* Incorporated project “evidence of success” metrics (PR #392)

  * Deployment & Infrastructure checks (CI/CD, containerization, hosting/cloud)
  * Version Control analysis (average lines per commit, commit consistency)
  * Added tests

* Updated prompt flow defaults

  * Default to “yes” except for destructive/security-sensitive actions
  * Added configurable default parameter in config manager
  * Added testing for config manager and new prompt behavior

* Reworked resume and portfolio management flow

  * Generate resumes/portfolios after first analysis run
  * Replaced “Generate” with “Manage Resumes” and “Manage Portfolios”
  * Added view, edit, delete, and regenerate options
  * Added deletion support in DB manager
  * Added full testing for new functionality

* Created API documentation for all endpoints and responses

* Finished analysis pipeline test rewrites (integration testing for app)

* Upstream changes to support API implementation (PR #402)

  * Adjusted DB config for cascading
  * Added DB_Manager functions for resumes and portfolios
  * Reworked DB_Manager to raise errors instead of returning None
  * Updated tests and adjusted downstream code

* Implemented API and functional testing (PR #407)

* Implemented API integration testing using test_db (PR #444)

* UI design created in Canva

* Prepared and presented Milestone 2 presentation

* Improved incremental upload handling

  * Reworked filepath comparison logic to ensure consistent detection of updated analyses
  * Prevented incorrect duplication during incremental file uploads

* Expanded database deletion capabilities

  * Implemented endpoints for deleting resumes and portfolios
  * Added corresponding integration tests to validate new functionality

* Implemented duplicate file detection

  * Added logic to recognize duplicate uploads
  * Ensured the system maintains a single instance of identical files

* Updated project documentation

  * Added links to evaluation test files in the README
  * Included clear setup and execution instructions for running the application



### Burnup chart & Task Table
<img width="908" height="469" alt="image" src="https://github.com/user-attachments/assets/66ad7008-f681-499b-bef1-1d32c0163ed5" />

<img width="1362" height="570" alt="image" src="https://github.com/user-attachments/assets/d48e3dd3-2201-44ae-aab1-2148ab4bc797" />



### Test Report
<img width="1184" height="743" alt="image" src="https://github.com/user-attachments/assets/1fa71282-b5c0-437a-a039-bbc9f6fbd858" />


### In Progress
- The remaining UI work involves finalizing one page that was not included in the initial design plan. This page will allow users to access and manage previously generated analyses. All other UI components have been completed.

### Upcoming plans
- The team will continue progressing on the frontend setup and design while addressing any API-related integration issues that arise.
- Frontend implementation will become a shared focus next week. During the upcoming meeting, responsibilities will be assigned by feature area to ensure balanced workload distribution and alignment with the Milestone 3 deadline.
- At Monday’s meeting, tasks for frontend implementation will be formally distributed. Key priorities include maintaining the decoupling of the CLI from the system workflow and finalizing the setup and development approach for the React web application. The team will use the Milestone 3 requirements and peer testing feedback to guide planning for the next phase of development.
- With the current progress, the team is well-positioned to advance frontend development. Next week’s discussions will focus on refining the frontend architecture and determining an improved deployment strategy to replace the current preliminary setup.

### Reflections
In addition to the previously noted API integration work, the team completed several backend refinements during this period. Improvements were made to filepath comparison logic for incremental uploads to ensure consistent handling of updated analyses. Additional database endpoints were implemented to support deletion of portfolios and resumes, along with corresponding integration tests. The milestone requirement for detecting and consolidating duplicate files was also completed. Documentation was updated to provide clear instructions and test files for system evaluation.

This phase was compressed due to presentation preparation and the Milestone 2 deadline, which required concentrated effort near the end of the cycle. Several tasks emerged as implementation progressed, leading to a higher volume of pull requests than usual. Despite the time pressure, the team collaborated effectively to complete all required objectives and stabilize the backend before transitioning to frontend development.

With Milestone 2 finalized, the team is in a strong position to shift focus toward frontend implementation while maintaining backend stability. Careful coordination and steady progress will be essential as development continues under a tight timeline.
