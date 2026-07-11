# API Reference

## Base URL

| Environment | URL |
|-------------|-----|
| Development | `http://localhost:8000/api/v1` |
| Staging | `https://api-staging.pm-internship.gov.in/api/v1` |
| Production | `https://api.pm-internship.gov.in/api/v1` |

All endpoints are prefixed with `/api/v1`.

---

## Authentication

The API uses JWT (JSON Web Token) for authentication. Tokens are issued upon login and must be included in the `Authorization` header for protected endpoints.

### Header Format

```
Authorization: Bearer <access_token>
```

### Token Lifecycle

- **Access Token**: Valid for 30 minutes. Used for API requests.
- **Refresh Token**: Valid for 7 days. Used to obtain new access tokens without re-authentication.
- Tokens are signed with HS256 algorithm.

### Role-Based Access Control

| Role | Permissions |
|------|-------------|
| `candidate` | View own profile, update profile, view recommendations, view notifications |
| `employer` | Create/manage opportunities, view matches for own opportunities |
| `admin` | Full access: analytics, allocation runs, policy config, audit logs, user management |

---

## Endpoints

### Authentication

#### POST /auth/register

Register a new user account.

**Request:**
```json
{
  "email": "priya.sharma@example.com",
  "password": "SecurePass123!",
  "role": "candidate"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `email` | string | Yes | Valid email address |
| `password` | string | Yes | 8-128 characters |
| `role` | string | No | `candidate` (default), `employer`, or `admin` |

**Response (201 Created):**
```json
{
  "id": 1,
  "email": "priya.sharma@example.com",
  "role": "candidate",
  "is_active": true,
  "created_at": "2025-01-15T10:30:00Z",
  "updated_at": "2025-01-15T10:30:00Z"
}
```

**Error (409 Conflict):**
```json
{
  "detail": "Email already registered"
}
```

---

#### POST /auth/login

Authenticate and receive JWT tokens.

**Request:**
```json
{
  "email": "priya.sharma@example.com",
  "password": "SecurePass123!"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Error (401 Unauthorized):**
```json
{
  "detail": "Invalid email or password"
}
```

**Error (403 Forbidden):**
```json
{
  "detail": "Account is deactivated"
}
```

---

#### POST /auth/refresh

Obtain new tokens using a valid refresh token.

**Request:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

---

### Candidates

#### POST /candidates/

Create a candidate profile for the authenticated user. **Requires authentication.**

**Request:**
```json
{
  "full_name": "Priya Sharma",
  "phone": "+91-9876543210",
  "education": {
    "degree": "B.Tech",
    "institution": "IIT Delhi",
    "year_of_passing": 2024,
    "percentage_cgpa": 8.5,
    "field_of_study": "Computer Science"
  },
  "skills": ["Python", "Machine Learning", "Data Analysis", "SQL"],
  "location": "New Delhi",
  "district": "New Delhi",
  "state": "Delhi",
  "social_category": "general",
  "is_rural": false,
  "mobility_preferences": {
    "willing_to_relocate": true,
    "preferred_locations": ["Mumbai", "Bangalore", "Hyderabad"],
    "remote_work_ok": true,
    "max_commute_km": 30
  }
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "user_id": 1,
  "full_name": "Priya Sharma",
  "phone": "+91-9876543210",
  "education": {
    "degree": "B.Tech",
    "institution": "IIT Delhi",
    "year_of_passing": 2024,
    "percentage_cgpa": 8.5,
    "field_of_study": "Computer Science"
  },
  "skills": ["Python", "Machine Learning", "Data Analysis", "SQL"],
  "location": "New Delhi",
  "district": "New Delhi",
  "state": "Delhi",
  "social_category": "general",
  "is_rural": false,
  "resume_url": null,
  "profile_completion_score": 0.80,
  "mobility_preferences": {
    "willing_to_relocate": true,
    "preferred_locations": ["Mumbai", "Bangalore", "Hyderabad"],
    "remote_work_ok": true,
    "max_commute_km": 30
  },
  "created_at": "2025-01-15T10:35:00Z",
  "updated_at": "2025-01-15T10:35:00Z"
}
```

---

#### GET /candidates/

List candidate profiles with optional filters. **Requires authentication (admin).**

**Query Parameters:**

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `page` | int | 1 | Page number (≥1) |
| `page_size` | int | 20 | Items per page (1-100) |
| `state` | string | - | Filter by state |
| `social_category` | string | - | Filter by category (`general`, `obc`, `sc`, `st`, `ews`) |

**Response (200 OK):**
```json
{
  "items": [
    {
      "id": 1,
      "user_id": 1,
      "full_name": "Priya Sharma",
      "phone": "+91-9876543210",
      "education": {"degree": "B.Tech", "institution": "IIT Delhi"},
      "skills": ["Python", "Machine Learning"],
      "location": "New Delhi",
      "district": "New Delhi",
      "state": "Delhi",
      "social_category": "general",
      "is_rural": false,
      "resume_url": null,
      "profile_completion_score": 0.80,
      "mobility_preferences": null,
      "created_at": "2025-01-15T10:35:00Z",
      "updated_at": "2025-01-15T10:35:00Z"
    }
  ],
  "total": 142,
  "page": 1,
  "page_size": 20,
  "total_pages": 8
}
```

---

#### GET /candidates/me

Get the authenticated user's candidate profile.

**Response (200 OK):** Same as candidate response object.

---

#### PUT /candidates/me

Update the authenticated user's candidate profile.

**Request:** Same fields as POST /candidates/ (all optional).

**Response (200 OK):** Updated candidate response object.

---

#### GET /candidates/{candidate_id}

Get a candidate profile by ID. **Requires authentication (admin).**

**Response (200 OK):** Candidate response object.

---

#### GET /candidates/me/completion

Get profile completion details with improvement suggestions.

**Response (200 OK):**
```json
{
  "score": 0.70,
  "missing_fields": ["phone", "resume", "mobility_preferences"],
  "suggestion": "Complete your phone, resume, mobility_preferences to improve your matches."
}
```

---

### Opportunities

#### POST /opportunities/

Create a new internship opportunity. **Requires authentication (employer/admin).**

**Request:**
```json
{
  "title": "Data Science Intern",
  "description": "Work on real-world data science projects involving machine learning, data visualization, and statistical analysis. Mentorship from senior data scientists.",
  "sector": "Technology",
  "required_skills": ["Python", "Machine Learning", "Data Analysis", "SQL", "Statistics"],
  "location": "Bangalore",
  "state": "Karnataka",
  "district": "Bangalore Urban",
  "work_mode": "hybrid",
  "capacity": 10,
  "stipend": 25000.0,
  "duration_months": 6,
  "eligibility_criteria": {
    "min_education": "bachelors",
    "field_of_study": "Computer Science",
    "min_profile_completion": 0.6
  }
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "employer_id": 5,
  "title": "Data Science Intern",
  "description": "Work on real-world data science projects...",
  "sector": "Technology",
  "required_skills": ["Python", "Machine Learning", "Data Analysis", "SQL", "Statistics"],
  "location": "Bangalore",
  "state": "Karnataka",
  "district": "Bangalore Urban",
  "work_mode": "hybrid",
  "capacity": 10,
  "stipend": 25000.0,
  "duration_months": 6,
  "eligibility_criteria": {
    "min_education": "bachelors",
    "field_of_study": "Computer Science",
    "min_profile_completion": 0.6
  },
  "is_active": true,
  "created_at": "2025-01-15T11:00:00Z",
  "updated_at": "2025-01-15T11:00:00Z"
}
```

---

#### GET /opportunities/

List opportunities with filters and text search.

**Query Parameters:**

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `page` | int | 1 | Page number |
| `page_size` | int | 20 | Items per page |
| `sector` | string | - | Filter by sector |
| `state` | string | - | Filter by state |
| `work_mode` | string | - | `remote`, `hybrid`, or `onsite` |
| `is_active` | bool | true | Filter active/inactive |
| `search` | string | - | Full-text search on title |

**Response (200 OK):** Paginated list of opportunity response objects.

---

#### GET /opportunities/{opportunity_id}

Get an opportunity by ID.

**Response (200 OK):** Opportunity response object.

---

#### PUT /opportunities/{opportunity_id}

Update an opportunity. **Requires authentication (owner or admin).**

**Request:** Same fields as POST (all optional).

**Response (200 OK):** Updated opportunity response object.

---

#### DELETE /opportunities/{opportunity_id}

Soft-delete an opportunity (sets `is_active=false`). **Requires authentication (owner or admin).**

**Response (204 No Content)**

---

### Matching

#### GET /matching/recommendations

Get top-K opportunity recommendations for the authenticated candidate. **Requires authentication (candidate).**

**Query Parameters:**

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `top_k` | int | 10 | Number of recommendations (1-100) |

**Response (200 OK):**
```json
[
  {
    "id": 42,
    "candidate_id": 1,
    "opportunity_id": 5,
    "score": 0.8734,
    "score_breakdown": {
      "skill_similarity": 0.80,
      "location_preference": 1.0,
      "education_fit": 0.90,
      "sector_interest": 0.85,
      "social_equity": 0.50,
      "profile_completeness": 0.80
    },
    "explanation": "Strengths: Skill Similarity: 80%, Location Preference: 100%, Education Fit: 90%. Areas for improvement: Social Equity: 50%",
    "rank": 1,
    "status": "pending",
    "created_at": "2025-01-15T12:00:00Z",
    "updated_at": "2025-01-15T12:00:00Z"
  }
]
```

---

#### GET /matching/candidate/{candidate_id}

Get matches for a specific candidate. **Requires authentication (admin).**

**Query Parameters:**

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `top_k` | int | 10 | Number of matches (1-100) |

**Response (200 OK):** List of match response objects.

---

#### GET /matching/opportunity/{opportunity_id}

Get top matches for a specific opportunity. **Requires authentication (admin).**

**Query Parameters:**

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `top_k` | int | 10 | Number of matches (1-100) |

**Response (200 OK):** List of match response objects.

---

#### POST /matching/run

Trigger batch matching for all active candidates and opportunities. **Requires authentication (admin).**

**Response (202 Accepted):**
```json
{
  "message": "Batch matching completed",
  "total_matches": 4250,
  "candidates_processed": 150
}
```

---

### Allocation

#### POST /allocation/run

Trigger a new allocation cycle. **Requires authentication (admin).**

**Request:**
```json
{
  "cycle_name": "January 2025 Allocation",
  "config": {
    "max_per_candidate": 1,
    "max_per_opportunity": null,
    "fairness_enabled": true,
    "min_category_representation": 0.30
  },
  "dry_run": false
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `cycle_name` | string | Yes | Descriptive name for the cycle |
| `config` | object | No | Allocation configuration overrides |
| `dry_run` | bool | No | If true, creates cycle but skips optimization |

**Response (202 Accepted):**
```json
{
  "id": 3,
  "name": "January 2025 Allocation",
  "status": "completed",
  "config": {
    "max_per_candidate": 1,
    "fairness_enabled": true,
    "min_category_representation": 0.30
  },
  "started_at": "2025-01-15T14:00:00Z",
  "completed_at": "2025-01-15T14:02:30Z",
  "created_at": "2025-01-15T14:00:00Z",
  "updated_at": "2025-01-15T14:02:30Z"
}
```

---

#### GET /allocation/cycles

List recent allocation cycles.

**Query Parameters:**

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `limit` | int | 20 | Number of cycles (1-100) |

**Response (200 OK):**
```json
[
  {
    "id": 3,
    "name": "January 2025 Allocation",
    "status": "completed",
    "config": null,
    "started_at": "2025-01-15T14:00:00Z",
    "completed_at": "2025-01-15T14:02:30Z",
    "created_at": "2025-01-15T14:00:00Z",
    "updated_at": "2025-01-15T14:02:30Z"
  },
  {
    "id": 2,
    "name": "December 2024 Pilot",
    "status": "running",
    "config": null,
    "started_at": "2024-12-20T09:00:00Z",
    "completed_at": null,
    "created_at": "2024-12-20T09:00:00Z",
    "updated_at": "2024-12-20T09:00:00Z"
  }
]
```

---

#### GET /allocation/cycles/{cycle_id}

Get allocation cycle details.

**Response (200 OK):** Allocation cycle response object.

---

#### GET /allocation/cycles/{cycle_id}/results

Get allocation results for a specific cycle.

**Query Parameters:**

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `page` | int | 1 | Page number |
| `page_size` | int | 20 | Items per page |

**Response (200 OK):**
```json
{
  "items": [
    {
      "id": 101,
      "candidate_id": 1,
      "opportunity_id": 5,
      "match_id": 42,
      "allocation_cycle_id": 3,
      "status": "confirmed",
      "explanation": "Strong match: Skill Similarity 80%, Location Preference 100%",
      "allocated_at": "2025-01-15T14:01:00Z",
      "created_at": "2025-01-15T14:01:00Z",
      "updated_at": "2025-01-15T14:01:00Z"
    }
  ],
  "total": 120,
  "page": 1,
  "page_size": 20,
  "total_pages": 6
}
```

---

#### GET /allocation/cycles/{cycle_id}/stats

Get aggregate statistics for an allocation cycle.

**Response (200 OK):**
```json
{
  "cycle_id": 3,
  "total_allocated": 120,
  "total_confirmed": 95,
  "total_declined": 10,
  "total_waitlisted": 15,
  "avg_match_score": 0.7234,
  "unique_candidates": 120,
  "unique_opportunities": 35
}
```

---

### Admin

#### GET /admin/analytics/overview

Get system-wide analytics overview. **Requires authentication (admin).**

**Response (200 OK):**
```json
{
  "total_users": 250,
  "total_candidates": 200,
  "total_active_opportunities": 50,
  "total_matches": 4250,
  "average_match_score": 0.6842,
  "state_distribution": {
    "Maharashtra": 35,
    "Karnataka": 28,
    "Tamil Nadu": 22,
    "Delhi": 20,
    "Uttar Pradesh": 18
  },
  "category_distribution": {
    "general": 80,
    "obc": 55,
    "sc": 35,
    "st": 20,
    "ews": 10
  }
}
```

---

#### GET /admin/analytics/matching

Get matching-specific analytics. **Requires authentication (admin).**

**Response (200 OK):**
```json
{
  "total_matches": 4250,
  "average_score": 0.6842,
  "status_distribution": {
    "pending": 3800,
    "accepted": 300,
    "rejected": 100,
    "waitlisted": 50
  }
}
```

---

#### GET /admin/policy

Get current matching and fairness policy configuration. **Requires authentication (admin).**

**Response (200 OK):**
```json
{
  "matching_weights": {
    "skill_similarity": 0.30,
    "location_preference": 0.20,
    "education_fit": 0.15,
    "sector_interest": 0.15,
    "social_equity": 0.10,
    "profile_completeness": 0.10
  },
  "fairness": {
    "enabled": true,
    "social_category_boost": 0.15,
    "rural_boost": 0.10,
    "gender_parity_target": 0.40
  },
  "match_top_k": 50,
  "match_min_score": 0.1
}
```

---

#### GET /admin/audit-logs

Get audit logs with optional filters. **Requires authentication (admin).**

**Query Parameters:**

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `page` | int | 1 | Page number |
| `page_size` | int | 50 | Items per page (1-200) |
| `action` | string | - | Filter by action type |
| `entity_type` | string | - | Filter by entity type |

**Response (200 OK):**
```json
{
  "items": [
    {
      "id": 501,
      "user_id": 10,
      "action": "allocation.run",
      "entity_type": "allocation_cycle",
      "entity_id": 3,
      "details": {"cycle_name": "January 2025 Allocation", "total_allocated": 120},
      "ip_address": "10.0.1.45",
      "created_at": "2025-01-15T14:00:00Z"
    }
  ],
  "total": 1250,
  "page": 1,
  "page_size": 50,
  "total_pages": 25
}
```

---

### Notifications

#### GET /notifications/

List notifications for the authenticated user. **Requires authentication.**

**Query Parameters:**

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `page` | int | 1 | Page number |
| `page_size` | int | 20 | Items per page |
| `unread_only` | bool | false | Filter to unread notifications |

**Response (200 OK):**
```json
{
  "items": [
    {
      "id": 101,
      "type": "in_app",
      "subject": "New Internship Match!",
      "body": "You have been matched with Data Science Intern at TechCorp. Score: 87%",
      "status": "pending",
      "sent_at": "2025-01-15T12:05:00Z",
      "created_at": "2025-01-15T12:05:00Z"
    }
  ],
  "total": 15,
  "page": 1,
  "page_size": 20,
  "total_pages": 1
}
```

---

#### PUT /notifications/{notification_id}/read

Mark a single notification as read. **Requires authentication.**

**Response (200 OK):**
```json
{
  "message": "Notification marked as read"
}
```

---

#### PUT /notifications/read-all

Mark all notifications as read. **Requires authentication.**

**Response (200 OK):**
```json
{
  "message": "All notifications marked as read"
}
```

---

## Error Codes Reference

| HTTP Code | Error | Description |
|-----------|-------|-------------|
| 400 | `Bad Request` | Invalid request body or parameters |
| 401 | `Unauthorized` | Missing or invalid authentication token |
| 403 | `Forbidden` | Insufficient permissions for the action |
| 404 | `Not Found` | Resource does not exist |
| 409 | `Conflict` | Resource already exists (e.g., duplicate email) |
| 422 | `Unprocessable Entity` | Validation error on request fields |
| 429 | `Too Many Requests` | Rate limit exceeded |
| 500 | `Internal Server Error` | Unexpected server error |

### Error Response Format

```json
{
  "detail": "Human-readable error message"
}
```

### Validation Error Format (422)

```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "value is not a valid email address",
      "type": "value_error.email"
    }
  ]
}
```

---

## Rate Limiting

| Endpoint Category | Limit | Window |
|-------------------|-------|--------|
| Authentication | 10 requests | per minute |
| Read endpoints | 100 requests | per minute |
| Write endpoints | 30 requests | per minute |
| Admin endpoints | 50 requests | per minute |

Rate limit headers are included in responses:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 97
X-RateLimit-Reset: 1705312800
```
