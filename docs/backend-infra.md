# Backend and Infrastructure Notes

This document describes how the **Cognito.ai monorepo** is wired today and how the **target** production stack should look.

## Repository layout

| Path | Role |
|------|------|
| `cognito-ai/` | Next.js 16 frontend (App Router). Browser calls `/api/...` on the same origin. |
| `backend/` | Django REST API, agentic skill runner (`backend/agent/runner.py`), auth/roadmap/lesson views. |
| `docs/` | Product, API contracts, schema targets, and planning. |

The frontend does **not** embed API route handlers for learning APIs. `cognito-ai/next.config.ts` rewrites `/api/:path*` to `${NEXT_PUBLIC_BACKEND_URL}/api/:path*` (default `http://localhost:8000`). For local work, run Django on that host/port or set `NEXT_PUBLIC_BACKEND_URL` in `cognito-ai/.env.local`.

## Frontend environment

| Variable | Purpose |
|----------|---------|
| `NEXT_PUBLIC_BACKEND_URL` | Base URL of the Django API (no trailing slash). Used only for the rewrite target. |

## Django backend environment

Copy `backend/.env.example` to `backend/.env` and set at least:

| Variable | Purpose |
|----------|---------|
| `DJANGO_SECRET_KEY` | Django secret. |
| `OPENROUTER_API_KEY` | Enables live skill calls; if empty, roadmap/lesson flows use fixtures where implemented. |
| `DECOMPOSER_MODEL`, `LESSON_GENERATOR_MODEL`, `SOCRATIC_TUTOR_MODEL` | Per-skill OpenRouter model IDs (see `backend/README.md`). |
| `AUTH_STUB_ALLOW_FIREBASE_FALLBACK` | Dev-friendly Firebase token handling; tighten for production. |

Optional / target persistence:

| Variable | Purpose |
|----------|---------|
| `DATABASE_URL` | Postgres (e.g. Supabase) when ORM-backed storage is wired. |
| `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY` | Only if the backend uses Supabase APIs directly (not required for Postgres-only). |

## Current persistence vs target

**Today (check `README.md` at repo root for the latest):**

- Lesson content and evaluation paths use **in-memory** caches inside the Django process where noted in `backend/README.md`.
- Auth endpoints can use **stub** stores for local development.
- ORM models and `docs/data-schema.md` describe the **intended** relational model; full Supabase-backed persistence is not the whole story yet.

**Target:**

- Supabase Postgres (or any managed Postgres) as the primary database for Django.
- `DATABASE_URL` with `sslmode=require` in production; pooling compatible with your host (e.g. Supabase pooler).
- Schema evolution via **Django migrations**, not ad hoc production SQL.

Example `DATABASE_URL` pattern:

```
DATABASE_URL=postgresql://<user>:<password>@<host>:<port>/<db>?sslmode=require
```

## Django settings (when `DATABASE_URL` is enabled)

- Prefer a single `DATABASE_URL` (e.g. via `dj-database-url`) for configuration.
- Run migrations the same way as against any Postgres:

```
python manage.py makemigrations
python manage.py migrate
```

## Security notes

- Never expose Django secrets, `OPENROUTER_API_KEY`, or Supabase service role keys in the Next.js bundle. Only `NEXT_PUBLIC_*` vars belong in the frontend.
- The frontend currently stores a **Firebase user id** in `localStorage` and sends it as `Authorization: Bearer ...` on API calls; aligning this with backend-issued sessions is tracked in the root `README.md` “Planned” section.
