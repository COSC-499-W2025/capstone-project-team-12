# Artifact Mining API — Documentation

API Endpoints can be viewed through the FastAPI documentation. Once the FastAPI live server is started in the container, view base URL at `http://localhost:8080/` and interactive docs can be found at `http://localhost:8080/docs#/`.

---

## Overview

Core workflow:
1. **Upload** a project archive via the two-phase upload flow → an `analysis_id` (UUID) is returned after Phase 1.
2. **Review** extracted topics and projects, then **commit** via Phase 2 to generate the AI summary.
3. **Generate** resumes and/or portfolios from the completed analysis.
4. **Edit or delete** any artifact as needed.

---

## Authentication & Consent

Some endpoints require **LLM consent** before they will succeed. Consent can be passed inline in the commit body (`online_llm_consent` field) or pre-set via `/privacy-consent`. If consent is missing, affected endpoints return `422`.

---

## Endpoints

### Health

#### `GET /`
Returns the API status.

**Response `200`**
```json
{ "status": "active" }
```

---

### Projects

#### `GET /projects`
Fetch a summary list of all analysed projects.

**Response `200`**
```json
[
  {
    "analysis_id": "uuid-string",
    "project_data": { ... }
  }
]
```

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
| `500` | Database error |

---

#### `DELETE /projects`
Wipe **all** analyses and associated data from the database. Use with caution.

**Response `204`** — All data deleted.

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
| `500` | Merge or extraction error |

---

#### `POST /projects/{analysis_id}/update/commit`
**Phase 2 — Commit & Generate.** Applies user edits to the cached extraction data, generates the AI summary, and persists everything to the database.

| Path Param | Type | Description |
|---|---|---|
| `analysis_id` | string (UUID) | The analysis being updated |

**Request Body** (`application/json`) — [`CommitUpdateRequest`](#commitupdaterequest)
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
Aggregate skill/technology counts across all analysed projects, drawn from language stats, skill stats, and import summaries.

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

---

### Resumes

#### `GET /resumes`
Returns all resumes in the database.

**Response `200`** — Array of resume objects.

---

#### `GET /resumes/{analysis_id}`
Returns all resumes associated with a specific analysis.

| Path Param | Type | Description |
|---|---|---|
| `analysis_id` | string (UUID) | Parent analysis ID |

| Code | Meaning |
|---|---|
| `200` | Array of resume objects |
| `400` | Invalid UUID |
| `404` | Analysis not found |
| `500` | Server error |

---

#### `GET /resume/{resume_id}`
Returns a specific resume by integer ID.

| Path Param | Type | Description |
|---|---|---|
| `resume_id` | integer | Resume ID |

| Code | Meaning |
|---|---|
| `200` | Resume object |
| `404` | Not found |
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
| `422` | LLM consent not set |
| `500` | Build or save error |

---

#### `PUT /resume/{resume_id}`
Update an existing resume's title and/or content.

| Path Param | Type | Description |
|---|---|---|
| `resume_id` | integer | Resume to update |

**Request Body** (`application/json`) — [`ResumeEditRequest`](#resumeeditrequest)

**Response `204`** — Updated. Header: `Location: /resume/{resume_id}`

---

#### `DELETE /resume/{resume_id}`
Delete a specific resume by ID.

| Path Param | Type | Description |
|---|---|---|
| `resume_id` | integer | Resume to delete |

| Code | Meaning |
|---|---|
| `204` | Deleted |
| `404` | Not found |
| `500` | Database error |

---

### Portfolios

Portfolio endpoints mirror the resume endpoints exactly, substituting `portfolio` for `resume`. The same LLM consent requirement applies to generation.

#### `GET /portfolios`
Returns all portfolios in the database. **Response `200`** — Array of portfolio objects.

#### `GET /portfolios/{analysis_id}`
Returns all portfolios for a given analysis. Same path param and response codes as `GET /resumes/{analysis_id}`.

#### `GET /portfolio/{portfolio_id}`
Returns a specific portfolio by integer ID. Same param and response codes as `GET /resume/{resume_id}`.

#### `POST /portfolio/generate/{analysis_id}`
Generate and save a new portfolio for the given analysis.

> [!NOTE] Requires LLM consent to be set via `/privacy-consent` first.

| Query Param | Type | Required | Description |
|---|---|---|---|
| `portfolio_title` | string | Optional | Optional display title |

**Response `201`** — Body: generated portfolio object. Header: `Location: /portfolio/{portfolio_id}`

#### `PUT /portfolio/{portfolio_id}`
Update an existing portfolio. **Request Body** ([`PortfolioEditRequest`](#portfolioeditrequest)). **Response `204`** — Updated.

#### `DELETE /portfolio/{portfolio_id}`
Delete a portfolio by ID. **Response `204`** — Deleted.

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

---

## Data Models

### `CommitUpdateRequest`
Used by both commit endpoints (`/upload/commit` and `/update/commit`).

| Field | Type | Required | Description |
|---|---|---|---|
| `topic_keywords` | array of [`TopicKeyword`](#topickeyword) | Required | Reviewed/edited topic keywords from Phase 1 |
| `user_highlights` | array of strings | Required | User-written highlight statements |
| `selected_projects` | array of strings | Required | Ordered list of project/repo names to include |
| `online_llm_consent` | boolean | Required | Must be `true` for AI summary generation |

### `TopicKeyword`
| Field | Type | Required | Description |
|---|---|---|---|
| `topic_id` | integer | Required | Index of the topic |
| `keywords` | array of strings | Required | Keywords describing this topic |

### `ResumeEditRequest`
| Field | Type | Required | Description |
|---|---|---|---|
| `resume_title` | string | Optional | Display title |
| `resume_data` | object | Required | Full resume content (freeform JSON) |

### `PortfolioEditRequest`
| Field | Type | Required | Description |
|---|---|---|---|
| `portfolio_title` | string | Optional | Display title |
| `portfolio_data` | object | Required | Full portfolio content (freeform JSON) |

### `ConsentRequest`
| Field | Type | Required | Description |
|---|---|---|---|
| `consent_type` | string | Required | Preference key to update (e.g. `"online_llm_consent"`) |
| `value` | boolean | Required | `true` to grant, `false` to revoke |

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