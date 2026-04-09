# Implementation Rules

## Goals

Deliver a **Next.js App Router** frontend (`cognito-ai/`) and **Django REST** backend (`backend/`) that enforce Socratic learning, keep performance high, and persist learner progress with reliable data contracts. Use **Supabase Postgres** (or equivalent Postgres) as the target database for Django. AI features use the **OpenRouter** tool-calling skill runner in `backend/agent/runner.py` and `backend/skills/*.py`.

## Repository Conventions

- Frontend: Next.js App Router under `cognito-ai/app/`.
- Backend: Django apps under `backend/apps/`.
- Keep global styles in app/globals.css only; component styles live in Tailwind classes.
- Public assets must remain under public/.
- Do not create barrel imports; import from the concrete module path.
- Prefer server components by default; isolate client state with "use client".

## TypeScript and Linting

- Use strict TypeScript typing for API payloads and shared UI models.
- Avoid "any" and implicit "any".
- Keep types in a single file per domain (for example, models/roadmap.ts).

## Performance Rules (Vercel Best Practices)

- Avoid request waterfalls: start independent fetches early and await them together.
- Prefer server components for data fetching; minimize data passed to client components.
- Use dynamic imports for heavy or rarely used components.
- Do not use barrel imports to avoid bundle bloat.
- Parallelize server data fetching whenever possible.

## Data Fetching and Caching

- Use server actions or API routes for mutations that need auth.
- Cache read-heavy server data with React.cache() when safe.
- Do not fetch the same data both in server and client for the same view.

## Database and Infra (Supabase / Postgres)

- Target: Supabase Postgres as the primary database for Django when persistence is enabled.
- Configure DB via `DATABASE_URL` (preferred) with `sslmode=require` in production.
- Run standard Django migrations against the configured database; avoid manual SQL edits to schema in production.
- Keep DB credentials and Supabase keys in **backend** environment variables only; never ship service role keys to the Next.js client bundle.

## State Management

- Keep page-level state minimal; prefer URL state for filters or search context.
- Use React context only for truly shared state (auth, theme, feature flags).

## Security and Privacy

- Validate Firebase ID tokens on the backend for every session exchange once the client uses `POST /api/auth/firebase-login` with real ID tokens.
- Validate email/password credentials on the backend for every login via the auth API.
- Never expose raw Firebase tokens or passwords to client logs.
- Never log or return raw passwords.
- Enforce per-user authorization on roadmaps and lesson states when data is DB-backed.
- **Current gap:** the frontend may send `Authorization: Bearer <firebase_uid>` from `localStorage` without a backend-issued `session_token`; tighten before production (see root `README.md`).

## Accessibility

- Every interactive element must have a visible focus state.
- Inputs require labels; icon buttons require aria-label.
- Hint controls must be keyboard accessible and screen-reader friendly.

## Error Handling

- Surface user-friendly messages for auth, network, and validation errors.
- Log detailed errors on the backend only; avoid client stack traces.

## Definition of Done

- Feature implements the product requirement and the design brief.
- API contract is updated in docs/api-contracts.md.
- Any new schema changes are documented in docs/data-schema.md.
- Performance rules above are not violated for the new feature.
