# Backend Runbook

## What This Is

Django REST backend for Cognito AI. Provides auth endpoints, AI-powered roadmap and lesson endpoints (via the agentic skill runner), and stub fallbacks for dev without API keys.

## Prerequisites

- Python 3.11+
- pip

## Setup

1. Create a virtual environment and activate it.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create a local env file:

```bash
cp .env.example .env
```

4. Set required values in `.env`. At minimum for dev:

| Variable | Description |
|---|---|
| `DATABASE_URL` | Django database connection string. Point this to Supabase Postgres for persistent auth/data storage. |
| `SUPABASE_URL` | Supabase project URL. Loaded for Supabase deployment configuration. |
| `SUPABASE_SERVICE_ROLE_KEY` | Supabase service role key. Keep this backend-only. |
| `DJANGO_SECRET_KEY` | Any random string |
| `OPENROUTER_API_KEY` | Required for live AI generation. Leave blank to use fixture fallbacks. |
| `DECOMPOSER_MODEL` | Model for roadmap decomposition. Defaults to `nvidia/nemotron-3-nano-30b-a3b:free` |
| `LESSON_GENERATOR_MODEL` | Model for lesson generation. Falls back to `DECOMPOSER_MODEL` if unset. |
| `SOCRATIC_TUTOR_MODEL` | Model for answer evaluation + hints. Falls back to `DECOMPOSER_MODEL` if unset. |
| `AUTH_STUB_ALLOW_FIREBASE_FALLBACK` | Set `true` for local dev |

## Run Locally

```bash
python manage.py runserver 0.0.0.0:8000
```

## Endpoints

| Method | Path | Description |
|---|---|---|
| POST | `/api/auth/register` | Register with email + password |
| POST | `/api/auth/login` | Login with email + password |
| POST | `/api/auth/firebase-login` | Exchange Firebase ID token for session |
| GET | `/api/roadmaps` | List the authenticated user’s roadmaps |
| POST | `/api/roadmaps` | Create and persist a roadmap for the authenticated user |
| GET | `/api/roadmaps/{roadmap_id}` | Fetch one roadmap owned by the authenticated user |
| GET | `/api/dashboard` | Aggregate lesson counts, progress summaries, and streak info |
| GET | `/api/lessons/{lesson_id}` | Fetch lesson micro-theory + questions for the authenticated user |
| POST | `/api/lessons/{lesson_id}/answer` | Submit answer, get Socratic evaluation + progress |
| POST | `/api/lessons/{lesson_id}/hint` | Request a tiered hint |

### Roadmap auth

- Send `Authorization: Bearer <session_token>` with roadmap requests.
- In local dev, the backend also accepts the Firebase UID fallback that the current frontend stores.

### Lesson auth and storage

- Send `Authorization: Bearer <session_token>` with lesson requests.
- Lesson content is stored in the `lessons` and `questions` tables.
- Lesson progress is stored in the `lesson_states` and `question_attempts` tables.
- Answer and hint requests update the saved lesson state for the authenticated user.

### POST /api/roadmaps

```json
// Request
{ "topic": "Machine Learning", "mode": "learn" }   // mode: "learn" | "solve", defaults to "learn"

// Response 201
{
  "roadmap_id": "<uuid4>",
  "mode": "learn",
  "modules": [
    { "id": "...", "title": "...", "outcome": "...", "index": 0 }
  ]
}
```

If `OPENROUTER_API_KEY` is not set, the endpoint returns a pre-built 5-module fixture — no errors.

Roadmaps are stored in the `roadmaps` and `modules` tables and returned in owner-scoped lists.

### GET /api/dashboard

```
GET /api/dashboard
```

Returns a dashboard summary for the authenticated user.

```json
{
  "summary": {
    "roadmaps_total": 2,
    "lessons_total": 3,
    "completed_lessons": 1,
    "in_progress_lessons": 1,
    "not_started_lessons": 1,
    "questions_total": 9,
    "questions_answered": 4,
    "question_attempts": 6,
    "xp_earned": 275,
    "stars_remaining": 5
  },
  "streak": {
    "current": 2,
    "longest": 4,
    "last_active_at": "2026-04-06T10:00:00+00:00"
  },
  "roadmaps": [],
  "lessons": [],
  "recent_activity": []
}
```

The dashboard endpoint requires `Authorization: Bearer <session_token>`.

### GET /api/lessons/{lesson_id}

```
GET /api/lessons/my-lesson-id?module_topic=Python+Loops&mode=learn
```

- If the lesson already exists for the authenticated user, the stored version is returned.
- If not stored, the `lesson_generator` skill is called to generate it and the lesson/questions are persisted.
- `answer_key` is never returned to the frontend — it is stored server-side for evaluation.

```json
// Response 200
{
  "lesson_id": "my-lesson-id",
  "mode": "learn",
  "micro_theory": "A loop repeats a block of code...",
  "questions": [
    { "id": "q1", "prompt": "What is a loop?", "difficulty": "easy" },
    { "id": "q2", "prompt": "When would you use a while loop?", "difficulty": "medium" },
    { "id": "q3", "prompt": "How do you avoid infinite loops?", "difficulty": "hard" }
  ]
}
```

The backend saves the attempt in `question_attempts` and updates the owning user's `lesson_states` row.

### POST /api/lessons/{lesson_id}/answer

```json
// Request
{ "question_id": "q1", "answer": "A loop repeats code while a condition is true." }

// Response 200
{
  "correct": true,
  "next_prompt": "Exactly! Now, how does a for loop differ from a while loop?",
  "progress": { "xp": 100, "stars_remaining": 3, "status": "in_progress" }
}
```

### POST /api/lessons/{lesson_id}/hint

```json
// Request
{ "question_id": "q1", "hint_level": 1 }   // hint_level: 1 (gentle) | 2 (partial) | 3 (strong)

// Response 200
{ "hint": "Think about what condition controls the loop.", "stars_remaining": 2 }
```

The backend stores the hint attempt and updates the user's lesson state.

**XP + Stars schedule:**

| Hints Used | XP Awarded | Stars Remaining |
|---|---|---|
| 0 (no hints) | 100 | 3 |
| 1 | 75 | 2 |
| 2 | 50 | 1 |
| 3 | 25 | 0 |
| Incorrect | 0 | — |

## Agentic Skill Architecture

Skills live in `backend/skills/*.py`. Each skill exports:
- `SPEC` — tool definition (name, description, JSON schema) sent to the model via OpenRouter
- `SYSTEM_PROMPTS` — per-mode system prompt (`learn` / `solve`)
- `run(params, mode)` — implementation called after the model selects the tool

The runner (`backend/agent/runner.py`) loads the skill, calls OpenRouter with `tool_choice: "required"`, extracts tool-call arguments, validates with Pydantic, and retries once on failure. Each skill has its own model env var in `SKILL_MODEL_MAP`.

### Registered Skills

| Skill | File | Model Env Var |
|---|---|---|
| `decomposer` | `skills/decomposer.py` | `DECOMPOSER_MODEL` |
| `lesson_generator` | `skills/lesson_generator.py` | `LESSON_GENERATOR_MODEL` |
| `socratic_tutor` | `skills/socratic_tutor.py` | `SOCRATIC_TUTOR_MODEL` |

To add a new skill: create `backend/skills/<skill_name>.py` and add an entry to `SKILL_MODEL_MAP` in `runner.py`.

## Firebase Stub Fallback Behavior

- Setting: `AUTH_STUB_ALLOW_FIREBASE_FALLBACK`
- If unset, fallback defaults to the value of `DJANGO_DEBUG`.
- Local development: `true` | Non-dev: `false`

When fallback is disabled and token verification fails, `POST /api/auth/firebase-login` returns `401`.

## Testing

Run all tests:

```bash
python manage.py test tests --verbosity=2
```

All tests mock network calls — no API key or internet connection required to run the full suite.

### Auth storage

- User records are stored in the `users` table.
- Session tokens are stored in the `auth_sessions` table.
- Firebase UID values are linked to local users on successful Firebase login.
