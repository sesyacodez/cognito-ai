# Data Schema

## users

- id: uuid, primary key
- firebase_uid: string, unique
- email: string
- name: string
- created_at: timestamp

## roadmaps

- id: uuid, primary key
- user_id: uuid, foreign key -> users.id
- topic: string
- created_at: timestamp

## modules

- id: uuid, primary key
- roadmap_id: uuid, foreign key -> roadmaps.id
- title: string
- index: int
- outcome: string

## lessons

- id: uuid, primary key
- module_id: uuid, foreign key -> modules.id
- title: string
- micro_theory: text

## questions

- id: uuid, primary key
- lesson_id: uuid, foreign key -> lessons.id
- prompt: text
- difficulty: string
- answer_key: text

## lesson_states

- id: uuid, primary key
- user_id: uuid, foreign key -> users.id
- lesson_id: uuid, foreign key -> lessons.id
- status: string
- stars_remaining: int
- xp_earned: int
- last_question_id: uuid, nullable
- updated_at: timestamp

## question_attempts

- id: uuid, primary key
- lesson_state_id: uuid, foreign key -> lesson_states.id
- question_id: uuid, foreign key -> questions.id
- answer: text
- correct: boolean
- hint_level: int
- created_at: timestamp
