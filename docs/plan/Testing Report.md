# Testing Report
## COSC-499-W2025 / capstone-project-team-12

---

## Table of Contents
1. [Testing Methodology](#testing-methodology)
2. [Frontend Tests](#frontend-tests)
3. [Backend Tests](#backend-tests)
    - [API Tests](#api-tests)
    - [File Processing](#file-processing)
    - [Text & Code Analysis](#text--code-analysis)
    - [Metadata](#metadata)
    - [LLM Integration](#llm-integration)
    - [Portfolio & Resume](#portfolio--resume)
    - [Project Analysis](#project-analysis)
    - [Configuration, Utilites & Database](#configuration-utilities--database)
4. [Test Results Screenshots](#test-results-screenshots)

---

## Testing Methodology

| Layer | Framework | Environment |
|---|---|---|
| Frontend | Vitest + React Testing Library | jsdom |
| Backend | Pytest (Python) | PostgreSQL test_db |

The suite covers four levels of testing: **unit** (isolated functions and components), **functional** (endpoint success and failure scenarios with realistic mocks), **integration** (database operations with a dedicated test_db), and **end-to-end** (complete workflows from file upload through portfolio generation).

---

## Frontend Tests

**Location:** `app/frontend/capstone-project-frontend/tests_frontend/`

---

### dashboard.test.tsx
| Area | What is tested |
|---|---|
| Rendering | Empty state, header, stats strip, and analysis cards |
| Counts | Correct analysis (3), resume (2), and portfolio (1) counts |
| Delete | Removes entries and updates stats in real time |
| Navigation | New analysis button triggers the onboarding modal |
| Toasts | Notifications display and dismiss correctly |

### fileImport.test.tsx
| Area | What is tested |
|---|---|
| Rendering | Heading, description, and drop zone |
| File selection | Manual input and drag-and-drop |
| File management | Filename and size displayed; files can be removed |
| Submission | POST to `/projects/upload/extract`; 500 errors handled gracefully |
| Button state | Confirm & Continue enabled only when a file is present |

### finetunePage.test.tsx
| Area | What is tested |
|---|---|
| Rendering | Project list, topic rows, and skill chips |
| Projects | Selection toggling on click |
| Topics | Keyword addition, removal, and full-row deletion |
| Skills | 3-skill maximum enforced; custom skills auto-selected if under limit |
| State | Saved state (`initialState`) takes priority over `extractedData` |
| Payload | Submitted payload structure validated |

### portfolio.test.tsx
| Area | What is tested |
|---|---|
| Rendering | Header, language bars, project cards, and framework timeline |
| Null handling | `null` portfolio_title renders as "Untitled Portfolio" |
| Mode toggle | Switches between public and private; edit buttons hidden in public mode |
| Search | Filters cards and language bars; shows empty state; clears on mode switch |
| Filter chips | Toggling chips hides the corresponding project card or section |

### projectInsights.test.tsx
| Area | What is tested |
|---|---|
| Rendering | Page heading and project buttons |
| Tabs | All four tabs visible; switching shows correct content |
| Data | Fetched and parsed on load; loading state shown while pending |

### resume.test.tsx
| Area | What is tested |
|---|---|
| Contact & Summary | Edit and save fields |
| Education & Awards | Add, remove, and edit entries |
| Skills | Add and remove; duplicates prevented |
| Projects & Languages | Edit names; display frameworks, insights, and file counts |
| Work Experience | Full CRUD including bullet point management |
| Async states | Loading, saving, and error states |
| Download | Opens the Resume Preview modal |

### resume.preview.test.tsx
| Area | What is tested |
|---|---|
| Rendering | Preview modal content displayed correctly |
| Close | Close button dismisses the modal |

### progress.test.tsx
| Area | What is tested |
|---|---|
| Rendering | Heading, subtext, and progress bar |
| Completion | `onComplete` callback fired when progress reaches 100% |

### commitHeatmap.test.tsx
| Area | What is tested |
|---|---|
| Rendering | Header, commit count, toggle buttons, and Less/More legend |
| Mode toggle | Switches between Commits and Lines Added; totals calculated correctly |
| Aggregation | Same-day commits aggregated into one cell |
| Date range | Project start and end dates shown in subheading |

---

## Backend Tests

**Location:** `app/backend/tests_backend/`

---

### API Tests

#### test_api_functional.py
Functional tests for all major endpoints using a `mock_backend` fixture that patches `DatabaseManager`, `ConfigManager`, `AnalysisPipeline`, and both LLM clients. Each endpoint has at least one success case and one or more failure cases.

| Area | What is tested |
|---|---|
| Projects CRUD | List, retrieve, delete; invalid UUID → 400, not found → 404, DB error → 500 |
| Resumes & Portfolios | Generate, list, retrieve, edit, delete; missing params, malformed UUIDs, and DB errors covered |
| Skills | Aggregated across analyses; empty DB returns `{"skills": {}}` |
| Config | GET and POST `/configs` for LLM consent preferences |
| Upload workflow | Extract phase caches pipeline state; commit phase restores it and generates AI summary |
| Update workflow | Incremental analysis update with tree merge and state re-caching |

#### test_api_integration.py
Sequential tests against a real `test_db`. An autouse fixture skips the suite if the correct database is not active. Tests carry IDs between steps to cover the full create → retrieve → edit → delete lifecycle for analyses, resumes, and portfolios, including cascade deletion and empty-list verification.

#### test_api_e2e.py
Three complete end-to-end workflows using a `make_new_analysis()` helper:

- **New Analysis** — extract → commit → list → retrieve → delete → verify 404
- **Resume** — generate → list → retrieve → edit → verify edit → delete → verify 404
- **Portfolio** — identical structure to the resume workflow

#### test_abort_endpoint.py
| Area | What is tested |
|---|---|
| Abort | Triggers correct cleanup of an in-progress analysis |
| Error cases | Non-existent or already-completed analyses handled gracefully |

---

### File Processing

#### test_file_manager.py
| Area | What is tested |
|---|---|
| Loading | Single files and directory traversal |
| Validation | Invalid paths and oversized files rejected |
| Archives | Nested zip extraction; RAR files rejected |
| Deduplication | Identical and zero-byte files deduplicated; works across sessions |
| Metadata | `created_at`, `last_modified`, and `file_hash` preserved |

#### test_file_classifier.py
| Area | What is tested |
|---|---|
| Classification | Files identified as code or text; results persist across operations |
| Tree operations | Filtering and node detachment by classification result |

#### test_tree_manager.py
| Area | What is tested |
|---|---|
| Merging | Identical, modified, new, and deleted files all handled correctly |
| Nested structures | Merging works across nested directory trees |

**Additional file processing tests:** `test_repo_detector.py`, `test_repository_analyzer.py`, `test_repository_processor.py`, `test_compare_paths.py`, and `test_validate_path.py` cover repository type detection, commit analysis with anonymised data, processing pipeline correctness, and path comparison and validation.

---

### Text & Code Analysis

#### test_text_preprocessor.py
| Area | What is tested |
|---|---|
| Preprocessing | Tokenisation, stopword filtering, and lemmatisation |
| Edge cases | Stopword-only and punctuation-only input; large files |

#### test_combined_preprocessor.py
| Area | What is tested |
|---|---|
| Integration | Text and code preprocessors combined into a single pipeline |
| Output | Combined output matches expected structure |

**Additional analysis tests:** `test_code_preprocessor.py`, `test_imports_extractor.py`, `test_topic_vectors.py`, and `test_bow_cache.py` cover code parsing, import extraction, topic vector generation, and bag-of-words cache serialisation.

---

### Metadata

#### test_metadata_extractor.py
| Area | What is tested |
|---|---|
| Extraction | Metadata extracted from disk files and binary/zipped content |
| Fallback | Fallback metadata returned when source file is missing |
| Content metrics | Line count, word count, character count, and MD5 checksum |
| Encoding | Detected automatically with fallback for unrecognised formats |

**Additional metadata tests:** `test_metadata_analyzer.py` aggregates statistics across a project; `test_stats_cache.py` validates JSON serialisation including conversion of non-serialisable types.

---

### LLM Integration

**Test files:** `test_llm_local.py`, `test_llm_online.py`, `test_user_prompts.py`, `test_pii_remover.py`

| Area | What is tested |
|---|---|
| Local & online inference | Requests and responses handled correctly; errors and timeouts caught |
| Prompt construction | Prompts built from user data and templates in the correct format |
| PII removal | Personally identifiable information stripped before LLM submission |

---

### Portfolio & Resume

**Test files:** `test_portfolio_builder.py`, `test_portfolio_data_processor.py`, `test_portfolio_editor.py`, `test_resume_builder.py`, `test_resume_data_processor.py`, `test_resume_editor.py`

| Area | What is tested |
|---|---|
| Generation | Portfolio and resume built correctly from project and metadata inputs |
| Data processing | Raw data transformed into the correct output shape |
| Editing | Fields updated and persisted to the database correctly |

---

### Project Analysis

#### test_project_success.py
| Area | What is tested |
|---|---|
| CI/CD & containerisation | Config files and Dockerfiles detected (case-insensitive) |
| Commit metrics | Average lines per commit and end-heavy distribution patterns identified |
| Missing data | Analyses with incomplete date information handled gracefully |

**Additional:** `test_repo_analysis_db_display.py` verifies repository analysis results are retrieved and displayed from the database correctly.

---

### Configuration, Utilities & Database

**Test files:** `test_config_manager.py`, `test_main_utils.py`, `test_user_selections.py`, `test_thumbnail.py`, `test_database_manager.py`, `test_db_utils.py`, `test_analysis_pipeline.py`

| Area | What is tested |
|---|---|
| Configuration | Loading, validation, and default value application |
| User selections | Parsing and validation of user input |
| Database | Connections, query execution, updates with `RETURNING`, and error handling |
| Pipeline | Stage ordering, output passing, and failure handling |
| Utilities | Thumbnail generation and core utility function correctness |

---

## Test Results Screenshots

#### Backend Tests:
<img width="1805" height="1056" alt="Backend Test Report" src="https://github.com/user-attachments/assets/dcdd0a35-f9f3-4dc0-9764-dca625fe6500" />

#### Frontend Tests:
##### Dashboard:
<img width="1616" height="1156" alt="image" src="https://github.com/user-attachments/assets/6948f48d-1f52-4d93-9d08-2ac0a6939302" />

##### File Import:
<img width="1666" height="602" alt="image" src="https://github.com/user-attachments/assets/66556735-3764-470a-ba52-14726e5d1b20" />

##### Finetuning
<img width="1788" height="1092" alt="image" src="https://github.com/user-attachments/assets/ecc96dca-b513-4a84-abe7-57ff34210c23" />

##### Heatmap
<img width="1680" height="582" alt="image" src="https://github.com/user-attachments/assets/e4730eb2-26c7-41d1-96d8-28e8041cc948" />

##### Resume and Resume Preview
<img width="1752" height="1312" alt="image" src="https://github.com/user-attachments/assets/a6babcbf-8d0e-489d-aac8-b63c012da3c6" />
<img width="1666" height="1054" alt="image" src="https://github.com/user-attachments/assets/a0b5c238-4b23-4f8d-8d6f-1cd0db1aaa67" />
<img width="1802" height="790" alt="image" src="https://github.com/user-attachments/assets/bd2366c5-ba47-49fb-b4e9-2869a71289dd" />

##### Portfolio
<img width="1564" height="1312" alt="image" src="https://github.com/user-attachments/assets/063f4a93-359d-41a0-98fd-0ff956911065" />
<img width="1726" height="612" alt="image" src="https://github.com/user-attachments/assets/85731c4f-cd80-4ba0-a731-d5e3b4643425" />

##### Progress Bar
<img width="1814" height="600" alt="image" src="https://github.com/user-attachments/assets/fb5e30ab-12e7-43ab-ba02-75ecd9fbf2e7" />

##### Project Insights
<img width="1786" height="692" alt="image" src="https://github.com/user-attachments/assets/7f054945-0fd8-4c71-993a-e3875714c16a" />

##### All Frontend Tests
<img width="1726" height="284" alt="image" src="https://github.com/user-attachments/assets/aff421c9-fdd7-423d-a71c-4a7defe69f8c" />

