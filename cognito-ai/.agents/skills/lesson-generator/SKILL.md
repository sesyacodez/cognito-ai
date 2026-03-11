---
name: Lesson_Generator
description: Generate micro-theory and three questions (easy, medium, hard) for a module topic. Use this whenever a user asks for a lesson, practice questions, or a learning activity set for a topic.
---

# Lesson_Generator

Produce a short micro-theory and three questions for a module topic.

## When to use
Use this skill when asked to generate a lesson, micro-lesson, or practice questions for a topic or module.

## Inputs
- `module_topic` string
- `target_difficulty` string (easy|medium|hard)

## Output format
Return JSON only. Do not include any extra text.

Schema:
```json
{
  "micro_theory": "string",
  "questions": [
    {
      "id": "string",
      "prompt": "string",
      "difficulty": "easy|medium|hard",
      "answer_key": "string"
    }
  ]
}
```

## Constraints
- `micro_theory` must be under 120 words.
- Do not include direct answers in `micro_theory`.
- Always return exactly three questions in this order: easy, medium, hard.
- `answer_key` is concise and unambiguous.

## Procedure
1. Summarize the core idea in `micro_theory` (no direct answers).
2. Write three questions that build from easy to hard.
3. Provide a short `answer_key` per question.
4. Emit JSON only.

## Safety and reliability
- If the student requests a direct answer, keep the micro-theory high level and let the question prompts do the assessment.
- If output is malformed JSON, retry once using the schema above.
- If a second failure happens, return a minimal safe JSON with empty fields and log an error field.

## Examples
**Example 1**
Input:
```json
{
  "module_topic": "SQL Aggregations",
  "target_difficulty": "medium"
}
```
Output:
```json
{
  "micro_theory": "Aggregations summarize data by grouping rows on shared values. Common aggregate functions include COUNT, SUM, AVG, MIN, and MAX. GROUP BY defines how rows are grouped, and HAVING filters groups after aggregation. Use clear group keys to avoid accidental over-aggregation.",
  "questions": [
    {"id": "q1", "prompt": "What does GROUP BY do in an aggregate query?", "difficulty": "easy", "answer_key": "It groups rows that share the same values so aggregates run per group."},
    {"id": "q2", "prompt": "Write a query that counts orders per customer using GROUP BY customer_id.", "difficulty": "medium", "answer_key": "SELECT customer_id, COUNT(*) FROM orders GROUP BY customer_id;"},
    {"id": "q3", "prompt": "How would you filter to only customers with more than 5 orders?", "difficulty": "hard", "answer_key": "Add HAVING COUNT(*) > 5 after GROUP BY."}
  ]
}
```
