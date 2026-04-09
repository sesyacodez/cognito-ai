# Cognito.ai — Next.js frontend

This directory is the **frontend package** inside the Cognito.ai monorepo. Authoritative architecture, endpoint status, and dev commands for the whole repo are in **[`../README.md`](../README.md)**.

## What lives here

- **App Router** routes: `/` (login), `/signup`, `/insight-hub`, `/workspace/[lessonId]`.
- **Firebase Auth** (Google + email/password) via `lib/AuthContext.tsx` and `lib/firebase.ts`.
- **API client** helpers: `lib/lessons.ts`, `lib/auth.ts` (local session + `Authorization` header).
- **PWA** via `@ducanh2912/next-pwa` and `next.config.ts`.

## How the app reaches the backend

Browser requests to **`/api/*`** are rewritten to **`NEXT_PUBLIC_BACKEND_URL`** (default `http://localhost:8000`). Run the Django app from `../backend/` on that origin, or point the env var at your deployed API.

## Commands

```bash
npm install
npm run dev
```

Open http://localhost:3000.

## Documentation (repo root)

- [Product requirements](../docs/PRD.md)
- [API contracts](../docs/api-contracts.md)
- [Backend / infra](../docs/backend-infra.md)
- [Data schema (target)](../docs/data-schema.md)
- [Implementation rules](../docs/implementation-rules.md)
