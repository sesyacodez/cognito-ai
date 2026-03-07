# API Contracts

## Auth

### POST /api/auth/register

- Purpose: create a local Django user with email/password and return a session.
- Request:

```
{
  "email": "string",
  "password": "string",
  "name": "string"
}
```

- Response:

```
{
  "session_token": "string",
  "user": {
    "id": "string",
    "email": "string",
    "name": "string"
  }
}
```

### POST /api/auth/login

- Purpose: exchange email/password for backend session.
- Request:

```
{
  "email": "string",
  "password": "string"
}
```

- Response:

```
{
  "session_token": "string",
  "user": {
    "id": "string",
    "email": "string",
    "name": "string"
  }
}
```

### POST /api/auth/firebase-login

- Purpose: exchange Firebase ID token for backend session.
- Request:

```
{
  "id_token": "string"
}
```

- Response:

```
{
  "session_token": "string",
  "user": {
    "id": "string",
    "email": "string",
    "name": "string"
  }
}
```

## Roadmaps

### GET /api/roadmaps

- Returns roadmaps for the authenticated user.

### POST /api/roadmaps

- Request:

```
{
  "topic": "string"
}
```

- Response:

```
{
  "roadmap_id": "string",
  "modules": [
    { "id": "string", "title": "string", "index": 0 }
  ]
}
```

### GET /api/roadmaps/{roadmap_id}

- Returns roadmap detail with modules and progress.

## Lessons

### GET /api/lessons/{lesson_id}

- Returns micro-theory and question set.

### POST /api/lessons/{lesson_id}/answer

- Request:

```
{
  "question_id": "string",
  "answer": "string"
}
```

- Response:

```
{
  "correct": true,
  "next_prompt": "string",
  "progress": {
    "xp": 0,
    "stars_remaining": 0,
    "status": "in_progress"
  }
}
```

### POST /api/lessons/{lesson_id}/hint

- Request:

```
{
  "question_id": "string",
  "hint_level": 1
}
```

- Response:

```
{
  "hint": "string",
  "stars_remaining": 0
}
```

## Dashboard

### GET /api/dashboard

- Returns lesson counts, streak info, and progress summaries.
