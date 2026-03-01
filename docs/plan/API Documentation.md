# Artifact Mining API — Documentation

API Endpoints can be viewed through the FastAPI documentation. Once the FastAPI live server is started in the container, you can view base URL at `http://localhost:8080/` and interactive docs can be found at `http://localhost:8080/docs#/`.

---

## Overview of Workflow

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

## Data Models

### Resume Object
Returned by `POST /resume/generate/{analysis_id}` and resume GET endpoints. The top-level object is stored in the `resume_data` column of the `Resumes` table.

```json
{
  "resume_id": "uuid-string",
  "analysis_id": "uuid-string",
  "summary": "string",
  "projects": [
    {
      "name": "string",
      "date_range": "string",
      "collaboration": "string",
      "frameworks": ["string"]
    }
  ],
  "skills": ["string"],
  "languages": [
    {
      "name": "string",
      "file_count": 0
    }
  ]
}
```

| Field | Type | Description |
|---|---|---|
| `resume_id` | string (UUID) | Auto-generated ID for this resume |
| `analysis_id` | string (UUID) | The analysis this resume was generated from |
| `summary` | string | AI-generated professional summary |
| `projects` | array | Top 3 projects extracted from the analysis |
| `projects[].name` | string | Project name |
| `projects[].date_range` | string | Project date range |
| `projects[].collaboration` | string | Collaboration description |
| `projects[].frameworks` | array of strings | Technologies used |
| `skills` | array of strings | Extracted skill categories |
| `languages` | array | Programming languages detected |
| `languages[].name` | string | Language name |
| `languages[].file_count` | integer | Number of files in that language |

---

### Portfolio Object
Returned by `POST /portfolio/generate/{analysis_id}` and portfolio GET endpoints. The top-level object is stored in the `portfolio_data` column of the `Portfolios` table.

```json
{
  "portfolio_id": "uuid-string",
  "result_id": "uuid-string",
  "projects_detail": [
    {
      "name": "string",
      "date_range": "string",
      "duration_days": 0,
      "user_role": { "role": "string", "blurb": "string" },
      "contribution": {
        "level": "string",
        "is_collaborative": false,
        "team_size": 0,
        "rank": 0,
        "percentile": 0,
        "contribution_share": 0.0
      },
      "statistics": {
        "commits": 0, "files": 0,
        "additions": 0, "deletions": 0, "net_lines": 0,
        "user_commits": 0, "user_lines_added": 0,
        "user_lines_deleted": 0, "user_net_lines": 0,
        "user_files_modified": 0
      },
      "testing": {
        "has_tests": false,
        "test_files": 0, "code_files": 0,
        "coverage_by_files": 0.0, "coverage_by_lines": 0.0
      },
      "frameworks": [{ "name": "string", "frequency": 0 }],
      "frameworks_summary": {
        "total_count": 0,
        "top_frameworks": ["string"],
        "has_more": false,
        "additional_count": 0
      }
    }
  ],
  "skill_timeline": {
    "high_level_skills": ["string"],
    "high_level_skills_meta": {
      "total_count": 0, "display_count": 0,
      "has_more": false, "additional_count": 0
    },
    "language_progression": [
      { "name": "string", "file_count": 0, "percentage": 0.0 }
    ],
    "language_meta": {
      "total_count": 0, "display_count": 0,
      "has_more": false, "additional_count": 0
    },
    "framework_timeline_list": [
      {
        "project_name": "string",
        "date_range": "string",
        "frameworks": ["string"],
        "total_frameworks": 0
      }
    ]
  },
  "growth_metrics": {
    "has_comparison": false,
    "earliest_project": "string",
    "latest_project": "string",
    "code_metrics": {
      "commit_growth": 0.0, "file_growth": 0.0,
      "lines_growth": 0.0, "user_lines_growth": 0.0
    },
    "technology_metrics": {
      "framework_growth": 0.0,
      "earliest_frameworks": 0,
      "latest_frameworks": 0
    },
    "testing_evolution": {
      "earliest_has_tests": false, "latest_has_tests": false,
      "coverage_improvement": 0.0, "testing_status": "string"
    },
    "collaboration_evolution": {
      "earliest_solo": true, "latest_solo": true,
      "earliest_team_size": 0, "latest_team_size": 0,
      "earliest_level": "string", "latest_level": "string",
      "collaboration_summary": "string"
    },
    "role_evolution": {
      "role_changed": false,
      "earliest_role": "string", "latest_role": "string"
    }
  }
}
```

| Field | Type | Description |
|---|---|---|
| `portfolio_id` | string (UUID) | Auto-generated ID for this portfolio |
| `result_id` | string (UUID) | The analysis this portfolio was generated from |
| `projects_detail` | array | Top 3 projects with deep-dive metrics |
| `skill_timeline` | object | Skill and language evolution across all projects |
| `skill_timeline.high_level_skills` | array of strings | Aggregated skill categories |
| `skill_timeline.language_progression` | array | Languages with file counts and percentages |
| `skill_timeline.framework_timeline_list` | array | Per-project framework usage over time |
| `growth_metrics` | object | Comparison between earliest and latest project |
| `growth_metrics.has_comparison` | boolean | `false` if fewer than 2 projects exist |
| `growth_metrics.code_metrics` | object | Growth percentages for commits, files, lines |
| `growth_metrics.testing_evolution` | object | Testing adoption and coverage changes |
| `growth_metrics.collaboration_evolution` | object | Team size and role changes |
| `growth_metrics.role_evolution` | object | Developer role changes across projects |

---

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