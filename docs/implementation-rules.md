# Implementation Rules

## Goals

Deliver a Next.js App Router frontend and Django REST backend that enforce Socratic learning, keep performance high, and persist learner progress with reliable data contracts. Use Supabase Postgres for persistence and a Nanoclaw agent (via OpenRouter) for AI-driven learning flows.

## Repository Conventions

- Use the Next.js App Router under app/.
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

## Database and Infra (Supabase)

- Use Supabase Postgres as the primary database for Django.
- Configure DB via `DATABASE_URL` (preferred) with `sslmode=require` in production.
- Run standard Django migrations against Supabase; avoid manual SQL edits to schema.
- Keep DB credentials and Supabase keys in environment variables only; never ship service role keys to the client.

## State Management

- Keep page-level state minimal; prefer URL state for filters or search context.
- Use React context only for truly shared state (auth, theme, feature flags).

## Security and Privacy

- Validate Firebase ID tokens on the backend for every session exchange.
- Validate email/password credentials on the backend for every login.
- Never expose raw Firebase tokens to client logs.
- Never log or return raw passwords.
- Enforce per-user authorization on roadmaps and lesson states.

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
