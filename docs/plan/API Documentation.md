# Artifact Mining API — Documentation

## Endpoints

### Health Check

#### `GET /`
Returns the API status.

**Response `200`**
```json
{ "status": "active" }
```

---

### Projects

#### `GET /projects`
Fetch all projects. Returns list of all analysed projects from tracked_data table.

**Response `200`**
```json
[
  {
    "analysis_id": "uuid-string",
    "project_data": { ... }
  }
]
```

| Code | Meaning |
|---|---|
| `200` | List of project summaries |
| `500` | Database error |

---

#### `GET /projects/{analysis_id}`
Fetch complete analysis data for a specific project.

| Path Param | Type | Description |
|---|---|---|
| `analysis_id` | string (UUID) | ID of the analysis |

| Code | Meaning |
|---|---|
| `200` | Full analysis data object |
| `400` | Invalid UUID format |
| `404` | Analysis not found |
| `422` | Validation error (malformed request) |
| `500` | Database error |

---

#### `DELETE /projects/{analysis_id}`
Delete a specific analysis and all associated data (resumes, portfolios, filesets, etc.).

| Path Param | Type | Description |
|---|---|---|
| `analysis_id` | string (UUID) | ID of the analysis to delete |

| Code | Meaning |
|---|---|
| `204` | Deleted |
| `400` | Invalid UUID format |
| `404` | Analysis not found |
| `422` | Validation error (malformed request) |
| `500` | Database error |

---

#### `DELETE /projects`
Wipe **all** analyses and associated data from the database. Use with caution.

| Code | Meaning |
|---|---|
| `204` | All data deleted |
| `500` | Database error |

---

### New Upload Flow

Uploading a new project uses a **two-phase flow**. Phase 1 extracts data and returns it for user review; Phase 2 commits the user's edits and generates the AI summary.

#### `POST /projects/upload/extract`
**Phase 1 — Upload & Extract.** Saves the uploaded file, runs the extraction pipeline (creating a new `analysis_id` internally), caches state for the commit step, and returns lightweight results to the frontend.

> **Content-Type:** `multipart/form-data`

| Field | Type | Required | Description |
|---|---|---|---|
| `file` | binary | Required | Project archive (e.g. `.zip`) |
| `github_username` | string | Optional | Optional GitHub username |
| `github_email` | string | Optional | Optional GitHub email |

**Response `200`**
```json
{
  "analysis_id": "uuid-string",
  "topic_keywords": [ ... ],
  "detected_skills": [ ... ],
  "analyzed_projects": [
    { "repository_name": "my-repo", "importance_score": 0.9 }
  ]
}
```

Present `topic_keywords` and `analyzed_projects` to the user for review before calling Phase 2.

| Code | Meaning |
|---|---|
| `200` | Extraction successful |
| `422` | Missing or malformed file input |
| `500` | Pipeline or server error |

---

#### `POST /projects/{analysis_id}/upload/commit`
**Phase 2 — Commit & Generate.** Applies user edits to the cached extraction data, generates the AI summary, and persists everything to the database.

| Path Param | Type | Description |
|---|---|---|
| `analysis_id` | string (UUID) | The ID returned by Phase 1 |

> **Request Body** (`application/json`) — [`CommitUpdateRequest`](#commitupdaterequest)
```json
{
  "topic_keywords": [
    { "topic_id": 0, "keywords": ["machine learning", "neural network"] }
  ],
  "user_highlights": ["Built a REST API with FastAPI"],
  "selected_projects": ["my-repo"],
  "online_llm_consent": true
}
```

**Response `200`**
```json
{ "status": "success", "summary": { ... } }
```

| Code | Meaning |
|---|---|
| `200` | Committed and saved |
| `404` | No cached Phase 1 data found (expired or wrong ID) |
| `422` | Validation error |
| `500` | Server error |

---

### Project Update Flow

Updating an existing analysis uses a **two-phase flow**, mirroring the upload flow but merging new files with the existing analysis.

#### `PUT /projects/{analysis_id}/update/extract`
**Phase 1 — Upload & Extract.** Merges the uploaded file with the existing analysis, runs extraction, and caches state for the commit step.

> **Content-Type:** `multipart/form-data`

| Path Param | Type | Description |
|---|---|---|
| `analysis_id` | string (UUID) | The existing analysis to update |

| Field | Type | Required | Description |
|---|---|---|---|
| `file` | binary | Required | New project archive to merge in |
| `github_username` | string | Optional | Optional GitHub username |
| `github_email` | string | Optional | Optional GitHub email |

**Response `200`**
```json
{
  "topic_keywords": [ ... ],
  "detected_skills": [ ... ],
  "analyzed_projects": [
    { "repository_name": "my-repo", "importance_score": 0.9 }
  ]
}
```

| Code | Meaning |
|---|---|
| `200` | Extraction successful |
| `400` | Invalid UUID format |
| `404` | Existing analysis not found |
| `422` | Missing or malformed file input |
| `500` | Merge or extraction error |

---

#### `POST /projects/{analysis_id}/update/commit`
**Phase 2 — Commit & Generate.** Applies user edits to the cached extraction data, generates the AI summary, and persists everything to the database.

| Path Param | Type | Description |
|---|---|---|
| `analysis_id` | string (UUID) | The analysis being updated |

> **Request Body** (`application/json`) — [`CommitUpdateRequest`](#commitupdaterequest)
```json
{
  "topic_keywords": [
    { "topic_id": 0, "keywords": ["machine learning", "neural network"] }
  ],
  "user_highlights": ["Achieved 95% test coverage"],
  "selected_projects": ["my-repo"],
  "online_llm_consent": true
}
```

**Response `200`**
```json
{ "status": "success", "summary": { ... } }
```

| Code | Meaning |
|---|---|
| `200` | Committed and saved |
| `404` | No cached Phase 1 data found (expired or wrong ID) |
| `422` | Validation error |
| `500` | Server error |

---

### Skills

#### `GET /skills`
Aggregate skill/technology counts across all analysed projects.

**Response `200`**
```json
{
  "skills": {
    "Python": 14,
    "pytest": 8,
    "React": 5
  }
}
```

Results are sorted by frequency (descending). `"Text only"` and `"Documentation"` categories are excluded.

| Code | Meaning |
|---|---|
| `200` | Skill counts returned |

---

### Resumes

#### `GET /resumes`
Returns all resumes in the database.

**Response `200`**
```json
[
  {
    "resume_id": 1,
    "resume_title": "string",
    "analysis_id": "uuid-string",
    "resume_data": { ... }
  }
]
```

| Code | Meaning |
|---|---|
| `200` | Array of resume objects |
| `404` | Internal lookup error |
| `500` | Server error |

---

#### `GET /resumes/{analysis_id}`
Returns all resumes associated with a specific analysis.

| Path Param | Type | Description |
|---|---|---|
| `analysis_id` | string (UUID) | Parent analysis ID |

**Response `200`** — Same structure as `GET /resumes`, filtered to the given analysis.

| Code | Meaning |
|---|---|
| `200` | Array of resume objects |
| `400` | Invalid UUID |
| `404` | Analysis not found |
| `422` | Malformed request |
| `500` | Server error |

---

#### `GET /resume/{resume_id}`
Returns a specific resume by integer ID.

| Path Param | Type | Description |
|---|---|---|
| `resume_id` | integer | Resume ID |

**Response `200`**
```json
{
  "resume_id": 1,
  "resume_title": "string",
  "analysis_id": "uuid-string",
  "resume_data": { ... }
}
```

| Code | Meaning |
|---|---|
| `200` | Resume object |
| `400` | Invalid resume_id (non-integer) |
| `404` | Not found |
| `422` | Malformed request |
| `500` | Server error |

---

#### `POST /resume/generate/{analysis_id}`
Generate and save a new resume for the given analysis.

> [!NOTE] Requires LLM consent to be set via `/privacy-consent` first.

| Path Param | Type | Description |
|---|---|---|
| `analysis_id` | string (UUID) | Source analysis |

| Query Param | Type | Required | Description |
|---|---|---|---|
| `resume_title` | string | Optional | Optional display title |

**Response `201`** — Body: generated resume object. Header: `Location: /resume/{resume_id}`

| Code | Meaning |
|---|---|
| `201` | Resume created |
| `400` | Invalid UUID |
| `404` | Analysis not found |
| `422` | LLM consent not set, or malformed request |
| `500` | Build or save error |

---

#### `PUT /resume/{resume_id}`
Update an existing resume's title and/or content.

| Path Param | Type | Description |
|---|---|---|
| `resume_id` | integer | Resume to update |

**Request Body** (`application/json`) — [`ResumeEditRequest`](#resumeeditrequest)

**Response `204`** — Updated. Header: `Location: /resume/{resume_id}`

| Code | Meaning |
|---|---|
| `204` | Updated |
| `422` | Malformed request body or invalid resume_id |
| `500` | Server error |

---

#### `DELETE /resume/{resume_id}`
Delete a specific resume by ID.

| Path Param | Type | Description |
|---|---|---|
| `resume_id` | integer | Resume to delete |

| Code | Meaning |
|---|---|
| `204` | Deleted |
| `400` | Invalid resume_id (non-integer) |
| `404` | Not found |
| `422` | Malformed request |
| `500` | Database error |

---

### Portfolios

Portfolio endpoints mirror the resume endpoints exactly, substituting `portfolio` for `resume`. The same LLM consent requirement applies to generation.

#### `GET /portfolios`
Returns all portfolios in the database. 

**Response `200`**
```json
[
  {
    "portfolio_id": 1,
    "portfolio_title": "string",
    "analysis_id": "uuid-string",
    "portfolio_data": { ... }
  }
]
```

| Code | Meaning |
|---|---|
| `200` | Array of portfolio objects |
| `404` | Internal lookup error |
| `500` | Server error |

#### `GET /portfolios/{analysis_id}`
Returns all portfolios for a given analysis. 

| Path Param | Type | Description |
|---|---|---|
| `analysis_id` | string (UUID) | Parent analysis ID |

**Response `200`** — Same structure as `GET /portfolios`, filtered to the given analysis.

| Code | Meaning |
|---|---|
| `200` | Array of portfolio objects |
| `400` | Invalid UUID format |
| `404` | Analysis not found |
| `422` | Malformed request |
| `500` | Server error |

#### `GET /portfolio/{portfolio_id}`
Returns a specific portfolio by integer ID. 

| Path Param | Type | Description |
|---|---|---|
| `portfolio_id` | integer | Portfolio ID |

**Response `200`**
```json
{
  "portfolio_id": 1,
  "portfolio_title": "string",
  "analysis_id": "uuid-string",
  "portfolio_data": { ... }
}
```

| Code | Meaning |
|---|---|
| `200` | Portfolio object |
| `400` | Invalid portfolio_id (non-integer) |
| `404` | Portfolio not found |
| `422` | Malformed request |
| `500` | Server error |

#### `POST /portfolio/generate/{analysis_id}`
Generate and save a new portfolio for the given analysis.

> [!NOTE] Requires LLM consent to be set via `/privacy-consent` first.

| Path Param | Type | Description |
|---|---|---|
| `analysis_id` | string (UUID) | Source analysis |

| Query Param | Type | Required | Description |
|---|---|---|---|
| `portfolio_title` | string | Optional | Optional display title |

**Response `201`** — Body: generated portfolio object. Header: `Location: /portfolio/{portfolio_id}`

| Code | Meaning |
|---|---|
| `201` | Portfolio created |
| `400` | Invalid UUID format |
| `404` | Analysis not found |
| `422` | LLM consent not set, or malformed request |
| `500` | Build or save error |

#### `PUT /portfolio/{portfolio_id}`
Update an existing portfolio. 

| Path Param | Type | Description |
|---|---|---|
| `portfolio_id` | integer | Portfolio to update |

**Request Body** (`application/json`) — [`PortfolioEditRequest`](#portfolioeditrequest)

**Response `204`** — Updated. Header: `Location: /portfolio/{portfolio_id}`

| Code | Meaning |
|---|---|
| `204` | Updated |
| `422` | Malformed request body or invalid portfolio_id |
| `500` | Server error |

#### `DELETE /portfolio/{portfolio_id}`
Delete a portfolio by ID. 

| Path Param | Type | Description |
|---|---|---|
| `portfolio_id` | integer | Portfolio to delete |

| Code | Meaning |
|---|---|
| `204` | Deleted |
| `400` | Invalid portfolio_id (non-integer) |
| `404` | Portfolio not found |
| `422` | Malformed request |
| `500` | Database error |

---

### Privacy / Consent

#### `POST /privacy-consent`
Record the user's LLM consent preference. Must be called before resume or portfolio generation (alternatively, pass `online_llm_consent` inline in the commit body).

**Request Body** (`application/json`) — [`ConsentRequest`](#consentrequest)
```json
{
  "consent_type": "online_llm_consent",
  "value": true
}
```

**Response `200`**
```json
{ "status": "success" }
```

| Code | Meaning |
|---|---|
| `200` | Preference saved |
| `422` | Malformed request body |

---

## Error Handling

All error responses follow this shape:

```json
{ "detail": "Human-readable error message" }
```

| Code | Meaning |
|---|---|
| `400` | Bad request (e.g. invalid UUID format) |
| `404` | Resource not found |
| `422` | Validation error or unmet precondition (e.g. missing LLM consent) |
| `500` | Internal server error |

FastAPI also returns `422` automatically for missing or malformed request bodies, with a `loc` path indicating which field failed.