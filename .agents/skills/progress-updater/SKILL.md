---
name: progress-updater
description: Update learner progress (XP, stars, status) after an answer is evaluated. Use this whenever correctness, hint usage, or timing must adjust progress and be persisted.
---

# progress-updater

Update learner progress based on correctness, hints, and timing, then persist it.

## When to use

Use this skill when a learner answer has been graded and progress must be updated and stored.

## Inputs

- `correct` boolean
- `hints_used` integer
- `time_ms` integer
- Current progress fields as needed (xp, stars_earned, status, stars_remaining)

## Output format

Return JSON only. Do not include any extra text.

Schema:

```json
{
  "progress": {
    "xp": 0,
    "stars_earned": 0,
    "status": "not_started|in_progress|completed"
  },
  "stars_remaining": 0,
  "persisted": true,
  "errors": []
}
```

## Constraints

- Always update XP and stars deterministically from the input signals.
- Persist updates through the backend API when available.

## Procedure

1. Calculate XP and stars from correctness, hint usage, and timing.
2. Update status based on lesson completion.
3. Persist via the backend API if available in the environment.
4. Emit JSON only.

## Safety and reliability

- If the persistence API is unavailable, set `persisted` to false and include a descriptive error in `errors`.
- If output is malformed JSON, retry once using the schema above.
- If a second failure happens, return a minimal safe JSON with zeros and log an error field.

## Examples

**Example 1**
Input:

```json
{
  "correct": true,
  "hints_used": 1,
  "time_ms": 42000,
  "progress": { "xp": 120, "stars_earned": 2, "status": "in_progress" },
  "stars_remaining": 1
}
```

Output:

```json
{
  "progress": { "xp": 135, "stars_earned": 3, "status": "in_progress" },
  "stars_remaining": 0,
  "persisted": true,
  "errors": []
}
```
