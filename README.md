# Cognito.ai

An adaptive, metacognitive learning platform that replaces direct answer-giving with Socratic, scaffolded tutoring. The goal is to help university students build real understanding by guiding them through structured roadmaps, micro-theory, and tiered hints.

## Product Vision

- Prevent AI-dependency by never giving direct answers.
- Decompose complex topics into a 5-module learning roadmap.
- Persist progress across lessons, including XP, stars, and lesson state.

## MVP Scope

- Google authentication via Firebase Auth and backend session exchange.
- Topic decomposition into exactly 5 modules with outcomes.
- Socratic lesson flow: micro-theory, 3 difficulty questions, tiered hints.
- Personal Insight Hub (Library) to resume progress.
- Progress persistence to a relational database.

## User Flow

1. Sign in with Google.
2. Enter a topic or a specific problem.
3. Review the generated roadmap and start a module.
4. Work through micro-theory and guided questions with hints.
5. Finish with reflection and save progress to the library.

## Experience Principles

- The AI mentor asks questions and never provides final answers.
- Hints consume stars and update state immediately.
- Clear loading, empty, and error states across lists and lessons.

## UI Layout Summary

- Insight Hub: topic/problem toggle, search bar with mic and upload icons, recent journeys.
- Interaction Screen: split layout with micro-theory on the left and chat on the right.
- Dashboard: progress overview and lesson tracking, accessible from the sidebar.
- Sidebar: Gemini-style navigation with search, toolbar, and recent journeys.
- Mobile: sidebar hidden by default and stacked theory + chat panels.

## Architecture Overview

The learning flow is managed by a LangGraph state machine, where each skill is a node that reads and updates shared state.

- `Decomposer`: generates a 5-module roadmap.
- `Lesson_Generator`: produces micro-theory and 3 questions (easy, medium, hard).
- `Socratic_Tutor`: evaluates responses and provides guiding questions or hints.
- `Progress_Updater`: persists XP, stars, and lesson state through the backend API.

## API Contracts (Backend)

- `POST /api/auth/firebase-login`: exchange Firebase ID token for backend session.
- `GET /api/roadmaps`: list roadmaps for the user.
- `POST /api/roadmaps`: create a roadmap for a topic.
- `GET /api/roadmaps/{roadmap_id}`: roadmap detail and progress.
- `GET /api/lessons/{lesson_id}`: fetch micro-theory and question set.
- `POST /api/lessons/{lesson_id}/answer`: submit answers and get next prompt.
- `POST /api/lessons/{lesson_id}/hint`: request a hint and update stars.
- `GET /api/dashboard`: progress summaries and streak info.

See [docs/api-contracts.md](docs/api-contracts.md) for request/response payloads.

## Data Model (Summary)

- Users, roadmaps, modules, lessons, questions.
- Lesson state and question attempts with hint usage and XP tracking.

See [docs/data-schema.md](docs/data-schema.md) for full schema details.

## Tech Stack

- Frontend: Next.js App Router + Tailwind CSS.
- Backend: Django REST Framework.
- Auth: Firebase Auth (Google OAuth).
- Database: PostgreSQL.
- Orchestration: LangGraph.
- AI Engine: OpenAI API (gpt-4o-mini).

## Repository Conventions

- Use the Next.js App Router under `app/`.
- Global styles live in `app/globals.css` only.
- Avoid barrel imports; import from concrete module paths.
- Prefer server components; isolate client state with `"use client"`.

See [docs/implementation-rules.md](docs/implementation-rules.md) for full rules.

## Getting Started

Install dependencies and run the development server:

```bash
npm install
npm run dev
```

Open http://localhost:3000 to view the app.

## Documentation Index

- [Product Requirements](docs/PRD.md)
- [Design Brief](docs/design-brief.md)
- [UI/UX Guidelines](docs/ui-ux-guidelines.md)
- [API Contracts](docs/api-contracts.md)
- [Data Schema](docs/data-schema.md)
- [Implementation Rules](docs/implementation-rules.md)
- [Agent Skills Spec](docs/agent-skills-spec.md)
