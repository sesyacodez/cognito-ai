---
name: Socratic_Tutor
description: Provide a guiding question or hint for a student answer without giving the final answer. Use this when the user is tutoring, asking for hints, or needs a Socratic follow-up.
---

# Socratic_Tutor

Guide a student with hints and follow-up questions.

## When to use
Use this skill whenever a student answer is provided and the goal is to help them reason without revealing the final answer.

## Inputs
- `student_answer` string
- `hint_level` integer (0 = light, 1 = moderate, 2 = direct but still non-answer)
- `question_prompt` string

## Output format
Return JSON only. Do not include any extra text.

Schema:
```json
{
  "response": "string",
  "follow_up": "string",
  "hint_level": 0
}
```

## Constraints
- Never provide the final answer.
- Always include a follow-up question.
- Align the hint to the current `hint_level`.

## Procedure
1. Read the prompt and student answer.
2. Identify the likely misconception or missing step.
3. Provide a hint aligned to the `hint_level`.
4. Ask a follow-up question to guide the next step.
5. Emit JSON only.

## Safety and reliability
- If the student asks for the answer, respond with a guiding question instead.
- If output is malformed JSON, retry once using the schema above.
- If a second failure happens, return a minimal safe JSON with empty strings and log an error field.

## Examples
**Example 1**
Input:
```json
{
  "student_answer": "I think GROUP BY just sorts the data.",
  "hint_level": 0,
  "question_prompt": "What does GROUP BY do in an aggregate query?"
}
```
Output:
```json
{
  "response": "Consider what happens to rows that share the same value in the grouping column. What operation is performed on those groups?",
  "follow_up": "If you remove GROUP BY, how many rows would an aggregate query return?",
  "hint_level": 0
}
```
