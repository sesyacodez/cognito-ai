# Backend Runbook

## What This Is

Django REST backend for Cognito AI. Provides auth endpoints, an AI-powered roadmap generation endpoint (via the agentic skill runner), and stub fallbacks for dev without API keys.

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
| `DJANGO_SECRET_KEY` | Any random string |
| `OPENROUTER_API_KEY` | Required for live AI roadmap generation. Leave blank to use fixture fallback. |
| `DECOMPOSER_MODEL` | Optional. Defaults to `nvidia/nemotron-3-nano-30b-a3b:free` |
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
| GET | `/api/roadmaps` | List roadmaps (returns `[]` stub) |
| POST | `/api/roadmaps` | Generate AI roadmap (or fixture fallback) |

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

If `OPENROUTER_API_KEY` is not set, the endpoint returns a pre-built 5-module fixture with the same shape — no errors.

## Agentic Skill Architecture

Skills live in `backend/skills/*.py`. Each skill exports:
- `SPEC` — tool definition (name, description, JSON schema) sent to the model via OpenRouter
- `SYSTEM_PROMPTS` — per-mode system prompt
- `run(params, mode)` — implementation called after the model selects the tool

The runner (`backend/agent/runner.py`) loads the skill, calls OpenRouter with `tool_choice: "required"`, extracts tool-call arguments, validates, and retries once on failure.

To add a new skill: create `backend/skills/<skill_name>.py` following the pattern above.

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

All tests mock network calls — no API key required to run the full suite.
