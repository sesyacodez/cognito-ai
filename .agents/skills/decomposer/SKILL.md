---
name: decomposer
description: Generate a learning roadmap with a variable number of modules based on topic complexity. Use this whenever the user wants a learning plan, course outline, curriculum, or module breakdown for a topic, even if they do not say "roadmap" explicitly.
---

# decomposer

Create a learning roadmap from a single topic with module count based on complexity.

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

- In `learn` mode, output 3-7 modules depending on topic breadth.
- In `solve` mode, output 1 module for simple tasks and 2-5 for complex tasks.
- Each `outcome` is a short, single-sentence learning outcome or concrete deliverable.
- `order` must be sequential starting at 1.

## Procedure

1. Read the topic.
2. Assess complexity and propose an appropriate progression from fundamentals to applied work.
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
      {
        "id": "m1",
        "title": "SQL Basics",
        "outcome": "Explain tables, rows, and columns and write simple SELECT queries.",
        "order": 1
      },
      {
        "id": "m2",
        "title": "Querying and Filtering",
        "outcome": "Use WHERE, ORDER BY, and LIMIT to retrieve the right records.",
        "order": 2
      },
      {
        "id": "m3",
        "title": "Aggregations and Joins",
        "outcome": "Summarize data with GROUP BY and combine tables with INNER and LEFT JOIN.",
        "order": 3
      }
    ]
  }
}
```
