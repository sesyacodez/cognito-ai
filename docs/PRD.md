# Product Requirement Document (PRD)

# Cognito.ai

## 1. Executive Summary

Cognito.ai is an adaptive, metacognitive learning platform that prevents "AI-dependency" by replacing direct answer-giving with a Socratic, scaffolded tutoring experience. Built for university students, it breaks down complex subjects into manageable roadmaps and guides users through interactive lessons using an autonomous AI agent.

## 2. Target Audience and Problem Statement

### Target Audience

- University students (especially first-year students in Lviv and beyond) who need to master complex subjects rather than just finding quick answers.

### Problem Statement

- General AI tools like ChatGPT often provide direct solutions, which can lead to passive learning and a lack of conceptual mastery.

## 3. Goals and Success Criteria

### Goals

- Encourage active learning through guided, Socratic instruction.
- Provide structured roadmaps that decompose complex topics into teachable modules.
- Persist learner progress so users can continue lessons over time.

### Success Criteria (MVP)

- Users can authenticate via Google or email/password and access personalized roadmaps.
- Each topic is decomposed into 5 modules with interactive lessons.
- Progress (XP, stars, lesson state) is saved and restored accurately.

## 4. Core Features (MVP)

- Dual Authentication: Secure login via Firebase Auth (Google OAuth) and Django email/password, integrated with the Django backend for session management.
- Smart Topic Decomposition: A "Decomposer" agent skill that analyzes broad topics and generates a 5-module learning roadmap.
- Socratic Learning Nodes: Interactive lesson modules consisting of brief theory, 3-tier difficulty questions, and a tiered hint system.
- Personal Insight Hub (Library): A dashboard where users can view their generated roadmaps, track progress, and resume saved lessons.
- Progress Persistence: Saving user performance data (stars, XP, and lesson states) to a relational database.

## 5. Technical Stack

| Component      | Technology                                          |
| -------------- | --------------------------------------------------- |
| Frontend       | Next.js (App Router) + React + Tailwind CSS         |
| Backend        | Django REST (Python), `backend/` in monorepo      |
| Authentication | Firebase Auth (Google OAuth) + email/password UI; backend session endpoints per `docs/api-contracts.md` |
| Database       | Supabase Postgres (target; persistence partial)     |
| AI             | OpenRouter tool-calling skill runner in backend     |

## 6. System Architecture and Agent Skills (CAI-19/20)

The project uses an OpenRouter-backed **agentic skill runner** in the Django backend to manage the learning flow. Instead of scattering prompts in views, the backend keeps discrete **skill modules** (`backend/skills/*.py`) that the runner exposes as tools to the model:

- Decomposer: Analyzes the input topic and returns a structured JSON roadmap.
- Lesson_Generator: Generates theory and questions for a specific subtopic.
- Socratic_Tutor: Evaluates student input and decides whether to provide a hint or advance the user.
- Progress_Updater: Updates the Supabase Postgres database with the user's latest performance stats.

## 7. Page-by-Page Requirements

- Auth Page (CAI-11, 18): Minimalist landing with "Sign in with Google" and email/password fields. Django verifies the Firebase ID token or validates email/password.
- Insight Hub / Dashboard (CAI-12, 15): Displays active roadmaps and a search bar for new topics. Fetches data from Django REST Framework.
- Learning Workspace (CAI-14): A vertical scrolling interface showing theory blocks, question cards, and the "Hint" trigger.
- Sidebar and Header (CAI-16): Global navigation for switching between the Library, Profile, and Settings.

## 8. Data Schema (Supabase Postgres via Django ORM)

- User Profile: Links Firebase UID to local user data.
- Roadmap: Stores the overarching topic and the 5 generated subtopic modules.
- Lesson State: Tracks which questions were answered, how many hints were used, and the final star rating.
