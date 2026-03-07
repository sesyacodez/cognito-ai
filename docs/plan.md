# Implementation Plan (Sprint-Based)

## Team

- Designer
- Backend/AI Engineer
- Backend Developer
- Frontend Developer

## Assumptions

- Sprints are 1 week (Friday to Thursday). Immediate plan covers the next 2 days.
- Stack: Next.js App Router, Tailwind, Django REST, PostgreSQL, Firebase Auth (Google OAuth) + Django password auth, OpenAI via LangGraph.
- API contracts in docs/api-contracts.md are the source of truth.

## Sprint 2 (Feb 27 - Mar 5, 2026) - Auth + Login MVP (Missed)

### Goals

- Login UI integrated with Google Auth and email/password.
- Backend session exchange endpoint live and tested.
- End-to-end login flow working in dev.

### Designer

- Finalize login page specs (states: idle, loading, error).
- Provide hover/focus/accessibility notes for the Google sign-in button.
- Provide states/specs for email/password fields and error copy.

### Frontend Developer

- Implement login page UI (in progress) and wire Google sign-in and email/password.
- Integrate POST /api/auth/firebase-login and POST /api/auth/login.
- Add registration UI and wire POST /api/auth/register.
- Handle error states and loading indicator.
- Add basic auth state storage (session token) for API requests.

### Backend Developer

- Implement POST /api/auth/firebase-login (per api-contracts.md).
- Implement POST /api/auth/login and POST /api/auth/register.
- Validate Firebase ID token and create session token.
- Validate email/password and create session token.
- Add user profile model linkage (Firebase UID -> local user).
- Add tests for token verification and error cases.
- Add tests for password auth and registration errors.

### Backend/AI Engineer

- Provide Firebase token verification helper (shared with backend dev).
- Define initial user schema fields (email, name, uid) if needed.

### Deliverables

- Login page functional in dev.
- Auth endpoint returns session token + user payload.
- Error handling and accessibility pass.

## Sprint 3a (Mar 6 - Mar 12, 2026) - Auth + Insight Hub + Roadmaps Core

### Goals

- Minimal auth + session flow working in dev (Google + email/password).
- Insight Hub (Library) page and data flow (basic layout).
- Roadmap creation and retrieval endpoints with per-user auth.
- End-to-end flow works with a placeholder 5-module response.

### Designer

- Finalize Insight Hub layout and empty state.
- Provide component specs for search bar, recent journeys, and sidebar.

### Frontend Developer

- Implement login page UI (minimal) and wire Google sign-in and email/password.
- Integrate POST /api/auth/firebase-login and POST /api/auth/login.
- Add registration UI and wire POST /api/auth/register.
- Add basic auth state storage (session token) for API requests.
- Build Insight Hub page (server components by default).
- Integrate GET /api/roadmaps and POST /api/roadmaps.
- Add basic sidebar/header navigation per design brief.

### Backend Developer

- Implement POST /api/auth/firebase-login (per api-contracts.md).
- Implement POST /api/auth/login and POST /api/auth/register.
- Validate Firebase ID token and create session token.
- Validate email/password and create session token.
- Add user profile model linkage (Firebase UID -> local user).
- Implement Roadmap models and endpoints (GET/POST /api/roadmaps).
- Enforce per-user authorization.
- Persist roadmap + module list.

### Backend/AI Engineer

- Provide Firebase token verification helper (shared with backend dev).
- Define initial user schema fields (email, name, uid) if needed.
- Define the roadmap module output shape and field validation rules.
- Provide a temporary fixed 5-module response for dev.

### Deliverables

- Users can log in and maintain a session in dev.
- Users can create and view roadmaps.
- Roadmap data persisted and authorized.
- UI and API flow demoable without AI.

## Sprint 3b (Mar 13 - Mar 19, 2026) - Decomposer + UX Polish

### Goals

- AI-powered roadmap generation.
- UI polish for Insight Hub components.
- Finish deferred auth tests and UI polish.

### Designer

- Finalize component specs for search bar, recent journeys, and sidebar.
- Provide motion and empty-state guidance for Insight Hub.

### Frontend Developer

- Polish Insight Hub components and empty states.
- Hook up roadmap creation to AI-generated modules when available.
- Improve login UI states and loading/error handling.

### Backend Developer

- Add validations and error handling for roadmap creation requests.
- Ensure module list persistence and response shape match contracts.
- Add tests for token verification and auth error cases.

### Backend/AI Engineer

- Implement Decomposer skill (LangGraph node) returning 5 modules.
- Wire Decomposer to POST /api/roadmaps.
- Add validations and retries for AI output shape.

### Deliverables

- Roadmaps generated via AI in dev.
- Insight Hub UI polished and consistent.

## Sprint 4 (Mar 20 - Mar 26, 2026) - Learning Workspace + Lesson Flow

### Goals

- Learning workspace UI with theory + Socratic chat.
- Lesson fetch, answer, and hint endpoints.

### Designer

- Finalize Interaction Screen layout (split view + hint controls).
- Provide mobile stacked layout rules.

### Frontend Developer

- Build Learning Workspace page and components.
- Integrate GET /api/lessons/{lesson_id}.
- Implement answer + hint flows with optimistic UI.

### Backend Developer

- Implement lesson models and endpoints:
  - GET /api/lessons/{lesson_id}
  - POST /api/lessons/{lesson_id}/answer
  - POST /api/lessons/{lesson_id}/hint
- Persist lesson state and progress updates.

### Backend/AI Engineer

- Implement Lesson_Generator and Socratic_Tutor nodes.
- Ensure tiered hints and difficulty levels match contract.
- Provide evaluation logic for answers and transitions.

### Deliverables

- Users can go through a lesson, answer questions, request hints.
- Progress updates saved and restored.

## Sprint 5 (Mar 27 - Apr 2, 2026) - Dashboard + Progress + Polish

### Goals

- Dashboard page with progress summaries.
- End-to-end progress persistence and UI polish.

### Designer

- Finalize Dashboard (Vercel v0 style) components and charts.
- Provide motion/stagger guidance for page load.

### Frontend Developer

- Build Dashboard page and integrate GET /api/dashboard.
- Add progress displays (XP, stars, streak).
- Accessibility audit and focus states.

### Backend Developer

- Implement /api/dashboard aggregation endpoint.
- Ensure data schema documented in docs/data-schema.md.
- Add integration tests for progress persistence.

### Backend/AI Engineer

- Implement Progress_Updater node and ensure consistent XP/stars.
- Add safety checks for lesson state transitions.

### Deliverables

- Dashboard and progress tracking complete.
- Data schema and API contracts updated.

## Cross-Sprint Checklist

- Update docs/api-contracts.md for any new fields.
- Document schema changes in docs/data-schema.md.
- Keep server components for data fetching; avoid client duplication.
- Verify accessibility: focus states, labels, aria-labels.
- Add basic e2e smoke tests for auth + roadmap + lesson flow.
