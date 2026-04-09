# Data Schema

**Status:** This is the **target** relational model for learner data (Supabase Postgres or any Postgres behind Django). The Django app under `backend/` may not yet persist every table here; some flows still use in-memory stores. See the repository root `README.md` for the current implementation snapshot.

Schema targets Supabase Postgres (managed Postgres) once fully wired.

**Sprint 5 note:** `lesson_states`, `question_attempts`, and `user_streaks` are currently backed by in-memory stores (`backend/utils/progress_store.py`). The shapes below match the in-memory dataclasses and will map directly to Django models + migrations when DB persistence is enabled.

## users

- id: uuid, primary key
- firebase_uid: string, unique, nullable
- auth_provider: string (firebase | password)
- password_hash: string, nullable
- email: string
- name: string
- created_at: timestamp

## auth_sessions

- id: uuid, primary key
- user_id: uuid, foreign key -> users.id
- token_hash: string, unique
- created_at: timestamp
- expires_at: timestamp
- revoked_at: timestamp, nullable

## roadmaps

- id: uuid, primary key
- user_id: uuid, foreign key -> users.id
- topic: string
- mode: string (learn | solve), default "learn"
- created_at: timestamp

## modules

- id: uuid, primary key
- roadmap_id: uuid, foreign key -> roadmaps.id
- title: string
- index: int
- outcome: string

## lessons

- id: uuid, primary key
- lesson_key: string, unique, public lesson identifier used by /api/lessons/{lesson_id}
- title: string
- module_topic: string
- mode: string (learn | solve)
- micro_theory: text
- created_at: timestamp
- updated_at: timestamp

## questions

- id: uuid, primary key
- lesson_id: uuid, foreign key -> lessons.id
- question_key: string, public question identifier returned by the API
- prompt: text
- difficulty: string (easy | medium | hard)
- answer_key: text
- position: int

## lesson_states

Tracks per-user, per-lesson progress. Status transitions are validated: `not_started → in_progress → completed`. Backward transitions are rejected.

- id: uuid, primary key
- user_id: uuid, foreign key -> users.id
- lesson_id: uuid, foreign key -> lessons.id
- status: string (not_started | in_progress | completed)
- stars_remaining: int (0-3, decremented per hint used)
- xp_earned: int (cumulative across all question attempts in this lesson)
- answered_questions: text[] (list of question IDs answered correctly)
- last_question_id: uuid, nullable
- created_at: timestamp
- updated_at: timestamp

### XP calculation (Progress_Updater skill)

| Condition | XP |
|---|---|
| Correct, 0 hints | 100 |
| Correct, 1 hint | 75 |
| Correct, 2 hints | 50 |
| Correct, 3 hints | 25 |
| Correct, 4+ hints | 10 |
| Incorrect | 0 |
| Speed bonus (≤30s) | +20 |

### Stars calculation

Stars start at 3 per lesson and are decremented by 1 for each hint tier used. Minimum is 0.

## question_attempts

- id: uuid, primary key
- lesson_state_id: uuid, foreign key -> lesson_states.id
- question_id: uuid, foreign key -> questions.id
- answer: text
- correct: boolean, nullable
- hint_level: int
- created_at: timestamp

## user_streaks (derived / cached)

Streak data is computed from `lesson_states.updated_at` dates. Currently tracked in-memory in `progress_store._activity_dates`.

- user_id: uuid, foreign key -> users.id
- current_streak: int (consecutive days with at least one lesson interaction)
- longest_streak: int
- last_active_date: date
