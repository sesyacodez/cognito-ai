# Cognito.ai

Adaptive learning platform focused on Socratic tutoring instead of direct answer-giving.

This repository is a monorepo with a Next.js frontend and a Django backend.

## Current State (April 2026)

This section reflects what is implemented in code today.

### Repository Architecture

- `cognito-ai/`: Next.js 16 (App Router) frontend.
- `backend/`: Django backend with auth, roadmap, and lesson endpoints.
- `docs/`: product, architecture, API contract, and planning documents.

### Frontend (Implemented)

Routes currently present:

- `/` login page (email/password UI + Google button).
- `/signup` registration page.
- `/insight-hub` main journey creation/list page.
- `/workspace/[lessonId]` lesson workspace.

Implemented UI behavior:

- Dark, dashboard-like layout with sidebar and journey list on Insight Hub.
- Topic vs Problem toggle when creating a journey.
- Lesson workspace with:
	- Micro-theory panel.
	- Question flow (easy/medium/hard).
	- Hint requests with star reduction.
	- Optimistic submit/hint UX.

Important integration note:

- Frontend auth state is currently managed with Firebase client SDK and local storage.
- Next.js rewrites `/api/*` to Django (`NEXT_PUBLIC_BACKEND_URL`, default `http://localhost:8000`).
- Backend auth endpoints exist, but frontend auth is not yet fully unified around backend-issued sessions.

### Backend (Implemented)

Live endpoints:

- `POST /api/auth/register`
- `POST /api/auth/login`
- `POST /api/auth/firebase-login`
- `GET /api/roadmaps`
- `POST /api/roadmaps`
- `GET /api/lessons/{lesson_id}`
- `POST /api/lessons/{lesson_id}/answer`
- `POST /api/lessons/{lesson_id}/hint`

Current backend behavior:

- Auth endpoints use stub/in-memory storage helpers for local workflow.
- `GET /api/roadmaps` returns an empty list placeholder.
- `POST /api/roadmaps` currently returns fixture-based 5-module output.
- Lesson endpoints call AI skills through the runner with fixture fallback on agent failure.
- Lesson cache is in-memory (process lifetime), not persistent DB storage.
- ORM models for users/roadmaps are placeholders and not implemented yet.

### AI Skill Runner Status

Skills implemented in `backend/skills/`:

- `decomposer.py`
- `lesson_generator.py`
- `socratic_tutor.py`

Runner implemented in `backend/agent/runner.py` with:

- OpenRouter tool-calling.
- Skill-specific model env vars.
- Retry-on-invalid-output behavior.

Not implemented yet:

- `progress_updater` skill and DB-backed progress persistence flow.

## Planned (From docs/plan.md and PRD)

Planned direction (not fully implemented yet):

- Replace roadmap fixtures with decomposer-driven generation in roadmap API.
- Persist users, roadmaps, lessons, and progress in Supabase Postgres via Django ORM.
- Add dashboard/progress endpoint and UI (`GET /api/dashboard`).
- Fully align frontend auth/session handling with backend session exchange.
- Complete end-to-end progress model (XP, stars, streaks, resumable lessons).
- Continue UX polish for Insight Hub and mobile adaptations.

## Tech Stack

- Frontend: Next.js 16, React 19, Tailwind CSS 4, Firebase Web SDK.
- Backend: Django 5, Django REST Framework, Pydantic, httpx.
- AI: OpenRouter tool-calling via backend skill runner.
- Database target: Supabase Postgres (planned integration is partial/in-progress).

## Local Development

### 1) Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py runserver 0.0.0.0:8000
```

### 2) Frontend

```bash
cd cognito-ai
npm install
npm run dev
```

Then open `http://localhost:3000`.

## Testing

Backend tests:

```bash
cd backend
python manage.py test tests --verbosity=2
```

Frontend lint:

```bash
cd cognito-ai
npm run lint
```

## Documentation Index

- Product requirements: [docs/PRD.md](docs/PRD.md)
- Design brief: [docs/design-brief.md](docs/design-brief.md)
- UI/UX guidelines: [docs/ui-ux-guidelines.md](docs/ui-ux-guidelines.md)
- API contracts (target): [docs/api-contracts.md](docs/api-contracts.md)
- Data schema (target): [docs/data-schema.md](docs/data-schema.md)
- Implementation rules: [docs/implementation-rules.md](docs/implementation-rules.md)
- Sprint plan: [docs/plan.md](docs/plan.md)
- Agent skills spec: [docs/agent-skills-spec.md](docs/agent-skills-spec.md)
