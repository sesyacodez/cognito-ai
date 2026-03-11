---
name: Decomposer
description: Generate a 5-module learning roadmap from a topic. Use this whenever the user wants a learning plan, course outline, curriculum, or module breakdown for a topic, even if they do not say "roadmap" explicitly.
---

# Decomposer

Create a 5-module learning roadmap from a single topic.

## When to use
Use this skill whenever the task is to break a topic into modules, outline a learning path, or propose a structured sequence of lessons.

## Inputs
- Topic string (preferred) or a state object containing `topic`.

## Output format
Return JSON only. Do not include any extra text.

Schema:
```json
{
  "roadmap": {
    "topic": "string",
    "modules": [
      {
        "id": "string",
        "title": "string",
        "outcome": "string",
        "order": 1
      }
    ]
  }
}
```

## Constraints
- Output exactly 5 modules.
- Each `outcome` is a short, single-sentence learning outcome.
- `order` must be 1 through 5.

## Procedure
1. Read the topic.
2. Propose a logical 5-step learning progression from fundamentals to applied work.
3. Write a clear title and one outcome per module.
4. Emit JSON only.

## Safety and reliability
- If asked for direct answers to learning questions, steer back to the roadmap structure.
- If output is malformed JSON, retry once using the schema above.
- If a second failure happens, return a minimal safe JSON with empty modules and log an error field.

## Examples
**Example 1**
Input:
```json
{
  "topic": "Intro to SQL"
}
```
Output:
```json
{
  "roadmap": {
    "topic": "Intro to SQL",
    "modules": [
      {"id": "m1", "title": "SQL Basics", "outcome": "Explain tables, rows, and columns and write simple SELECT queries.", "order": 1},
      {"id": "m2", "title": "Filtering Data", "outcome": "Use WHERE, AND, OR, and LIKE to filter query results.", "order": 2},
      {"id": "m3", "title": "Aggregations", "outcome": "Apply COUNT, SUM, AVG with GROUP BY and HAVING.", "order": 3},
      {"id": "m4", "title": "Joins", "outcome": "Combine tables with INNER and LEFT joins to answer multi-table questions.", "order": 4},
      {"id": "m5", "title": "Practical Queries", "outcome": "Write complete queries for real-world reporting scenarios.", "order": 5}
    ]
  }
}
```
