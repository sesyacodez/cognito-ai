# Agent Skills Specification

## Overview

The learning flow is implemented as a LangGraph state machine. Each skill is a node that reads and updates a shared state object.

## Shared State Shape

```
{
  "user_id": "string",
  "roadmap_id": "string",
  "module_id": "string",
  "lesson_id": "string",
  "topic": "string",
  "module_index": 0,
  "lesson_index": 0,
  "micro_theory": "string",
  "questions": [
    {
      "id": "string",
      "prompt": "string",
      "difficulty": "easy|medium|hard",
      "answer_key": "string"
    }
  ],
  "student_answer": "string",
  "hint_level": 0,
  "stars_remaining": 0,
  "progress": {
    "xp": 0,
    "stars_earned": 0,
    "status": "not_started|in_progress|completed"
  }
}
```

## Skill: Decomposer

- Input: topic string.
- Output: roadmap JSON with 5 modules and short learning outcomes.
- Constraints: must return exactly 5 modules.

## Skill: Lesson_Generator

- Input: module topic and target difficulty.
- Output: micro-theory plus 3 questions (easy, medium, hard).
- Constraints: no direct answers in micro-theory; keep under 120 words.

## Skill: Socratic_Tutor

- Input: student answer, hint level, question prompt.
- Output: a guiding question or a hint aligned to the current level.
- Constraints: never provide the final answer; always ask a follow-up.

## Skill: Progress_Updater

- Input: correctness signal, hint usage, and timing.
- Output: updated XP, stars, and lesson state.
- Constraints: persist updates to the database through the backend API.

## Safety and Reliability

- If the student requests direct answers, respond with a guiding question.
- If model output is malformed JSON, retry once with a strict schema.
- If repeated failure, return a minimal safe response and log error.
