# Implementation Plan (Sprint-Based)

## Team

- Designer
- Backend/AI Engineer
- Backend Developer
- Frontend Developer

## Assumptions

- Sprints are 1 week (Friday to Thursday). Immediate plan covers the next 2 days.
- Stack: Next.js App Router, Tailwind, Django REST, Supabase Postgres, Firebase Auth (Google OAuth) + Django password auth, Gemini via OpenRouter (agentic skill runner).
- API contracts in docs/api-contracts.md are the source of truth.
- Agent skills live in `backend/skills/*.py`; an agent runner in `backend/agent/runner.py` calls OpenRouter with skill specs as tools.

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

- Scaffold minimal Django project in backend/ (manage.py, config/, apps/users, apps/roadmaps, requirements.txt, .env.example).
- Provide Firebase token verification helper (backend/utils/firebase_auth.py, shared with backend dev).
- Wire temporary auth stubs (POST /api/auth/register, /api/auth/login, /api/auth/firebase-login) so frontend auth integration can proceed while backend implementation is pending.
- Define initial user schema fields (email, name, uid) - already complete in docs/data-schema.md.
- Define the roadmap module output shape and field validation rules (backend/utils/validators.py with Pydantic models). Includes order->index normalizer.
- Provide a temporary fixed 5-module response for dev (backend/utils/fixtures.py).
- Wire stub endpoints (GET and POST /api/roadmaps) so frontend dev can integrate without waiting for backend dev. Add CORS for Next.js dev server.
- Add unit tests for Firebase helper, validators, and fixtures.
- Add backend API contract smoke tests for auth and roadmap stub flows.
- Harden dev auth fallback behavior for firebase-login via env gating (AUTH_STUB_ALLOW_FIREBASE_FALLBACK; defaults to DJANGO_DEBUG when unset).
- Document backend local setup, stub endpoints, and validation commands in backend/README.md.

### Deliverables

- Users can log in and maintain a session in dev.
- Users can create and view roadmaps.
- Roadmap data persisted and authorized.
- UI and API flow demoable without AI.
- Stub API server (Django) serving placeholder roadmap responses for frontend integration.
- Stub auth API server (Django) serving register/login/firebase-login responses for frontend integration.
- API smoke test coverage for stub auth + roadmap contract paths.
- Env-gated Firebase fallback behavior documented for local vs non-dev environments.

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

- Create `backend/skills/` directory with one skill per file (spec + implementation).
- Implement `backend/skills/decomposer.py` — Decomposer skill, two modes:
  - **`learn`** mode: 3–7 modules with learning outcomes.
  - **`solve`** mode: 1–5 modules with concrete deliverables (1 module if problem is simple).
- Implement `backend/agent/runner.py` — agent runner that loads skill specs and calls OpenRouter (Gemini `nvidia/nemotron-3-nano-30b-a3b:free`) with them as tools; validates output; retries once on failure; raises `AgentError` on repeated failure.
- Wire Decomposer to `POST /api/roadmaps`: call `runner.run_skill("decomposer", topic, mode=mode)`; graceful fixture fallback on `AgentError`.
- Generate UUID4 for `roadmap_id` in `normalize_decomposer_output()`.
- Update `validators.py`: flexible module count (1–7), keep order uniqueness check.
- Add `httpx>=0.27,<1` to `requirements.txt`; add `DECOMPOSER_MODEL` and `OPENROUTER_API_KEY` notes to `.env.example`.
- Update unit tests in `tests/test_validators.py` for flexible count.
- Add `tests/test_decomposer.py`: happy path, retry, double-failure, missing API key.
- Update `tests/test_api_contract_smoke.py` to mock `runner.run_skill` and pass `mode`.

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

- Implement `backend/skills/lesson_generator.py` — Lesson_Generator skill:
  - Generates micro-theory (≤120 words) + 3 questions (easy/medium/hard) for a module topic.
  - For `solve` mode: theory is a problem brief; questions are guided implementation tasks.
- Implement `backend/skills/socratic_tutor.py` — Socratic_Tutor skill:
  - Evaluates student answer and returns a guiding question or tiered hint.
  - Never provides the direct answer.
- Wire both skills into the agent runner; update runner to support multi-skill context.
- Ensure tiered hints and difficulty levels match contracts.
- Provide evaluation logic for answer correctness and lesson state transitions.

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

- Implement Progress_Updater skill for the Nanoclaw agent and ensure consistent XP/stars.
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
