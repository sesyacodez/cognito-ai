# Agent Skills Specification

## Overview

The learning flow is driven by an **agentic skill runner** built into the Django backend (`backend/agent/runner.py`). Instead of hardcoding prompts per feature, the backend maintains discrete **skill files** (`backend/skills/*.py`). Each skill defines its own input schema and system prompt. The runner calls **OpenRouter** with the skill specs as **tools** (models are configured per skill via env vars). The model selects and invokes the appropriate skill; the runner executes it and returns the result.

This pattern means:
- No hardcoded prompts scattered through views
- Each skill is a self-contained, testable Python module
- Adding a new skill = adding one file in `backend/skills/`
- The LLM decides which skill to invoke based on context

## Agentic Architecture

```
Django view (e.g. POST /api/roadmaps)
  → agent/runner.py
      → Loads relevant skill specs (name, description, input schema)
      → Calls OpenRouter with skills as tools
      → Model selects a skill and returns structured arguments
      → Runner invokes the skill implementation
      → Validates output (Pydantic)
      → Returns result to view
```

## Shared Agent State Shape

Each skill reads from and may write to a shared state object passed through the runner:

```json
{
  "user_id": "string",
  "roadmap_id": "string",
  "mode": "learn|solve",
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

## Skill File Structure

Each skill lives in `backend/skills/<skill_name>.py` and exports:

```python
# Skill spec — sent to the model as a tool definition
SPEC = {
    "name": "skill_name",
    "description": "...",   # What the model reads to decide when to call this skill
    "parameters": { ... }   # JSON Schema for the skill's input
}

# Skill implementation — called by the runner when the model selects this skill
def run(params: dict, state: dict) -> dict:
    """Executes the skill. Returns result dict."""
```

---

## Skill: Decomposer

**File:** `backend/skills/decomposer.py`

- **Input:** `topic` (string) + `mode` (`learn` or `solve`)
- **Output:** roadmap with N modules and learning outcomes/deliverables
- **`learn` mode:** Divide the topic into 3–7 sequential learning modules. Each module has a clear learning outcome.
- **`solve` mode:** Assess problem complexity. If simple (single clear task), return 1 module framed as a guided project. If complex, return 2–5 modules as sequential work steps with concrete deliverables.
- **Constraints:** Module `order` values must be unique and sequential from 1; IDs are UUID4s.

---

## Skill: Lesson_Generator

**File:** `backend/skills/lesson_generator.py`

- **Input:** `module_topic` (string) + `target_difficulty` (`easy|medium|hard`) + `mode` (`learn|solve`)
- **Output:** micro-theory (≤120 words) plus 3 questions (easy, medium, hard).
- **`solve` mode:** Frame theory as a problem brief; questions as guided implementation tasks.
- **Constraints:** No direct answers in micro-theory; always ask a follow-up.

---

## Skill: Socratic_Tutor

**File:** `backend/skills/socratic_tutor.py`

- **Input:** `student_answer` (string) + `hint_level` (int) + `question_prompt` (string)
- **Output:** A guiding question or a hint aligned to the current hint level.
- **Constraints:** Never provide the final answer; always ask a follow-up.

---

## Skill: Progress_Updater

**File:** `backend/skills/progress_updater.py`

- **Input:** `correctness` (bool) + `hint_usage` (int) + `timing_seconds` (int)
- **Output:** Updated XP, stars, and lesson state.
- **Constraints:** Persist updates to Supabase Postgres through the backend API.

---

## Agent Runner

**File:** `backend/agent/runner.py`

```python
def run_skill(skill_name: str, topic: str, state: dict, **kwargs) -> dict:
    """
    Loads the skill spec for skill_name, calls OpenRouter with it as a tool,
    invokes the implementation, validates output, and returns the result dict.
    Retries once on malformed output. Raises AgentError on repeated failure.
    """
```

---

## Safety and Reliability

- If the model output is malformed JSON or fails schema validation, retry once with an explicit JSON-only instruction.
- If repeated failure, raise `AgentError` and let the view fall back gracefully (e.g. fixture response).
- If the student requests direct answers, the `Socratic_Tutor` skill responds with a guiding question.
