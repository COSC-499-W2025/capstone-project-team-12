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



### Burnup chart & Task Table
<img width="1109" height="574" alt="image" src="https://github.com/user-attachments/assets/452e3852-29d4-4509-be8a-dcd20bf72572" />



<img width="1408" height="606" alt="image" src="https://github.com/user-attachments/assets/7e2c5531-86ad-4eae-9f13-6c1fceb277fd" />


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
Over the past few weeks, the team’s primary focus was API integration. Because there were multiple possible implementation approaches and the work was divided among members, a few minor integration conflicts arose, which were resolved collaboratively.

All planned objectives for this period were completed, along with additional progress beyond the original scope. To support a smooth transition into Milestone 3, the UI design was finalized earlier than initially scheduled so frontend development could begin immediately with a shared vision. Additional implementation work was also taken on where capacity allowed, and certain responsibilities were redistributed to maintain momentum during a temporary team member absence.

With Milestone 2 complete, the team is well-positioned to transition into frontend development. Given the compressed timeline of the remaining weeks, careful planning and consistent progress tracking will be essential to ensure all Milestone 3 deliverables are identified, scheduled appropriately, and completed on time.
