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


### Upcoming plans


### Reflections
