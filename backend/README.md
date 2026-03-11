# Backend Runbook

## What This Is

This Django service currently provides Sprint 3a stub endpoints so the frontend can integrate before full backend implementation is complete.

## Prerequisites

- Python 3.11+
- pip

## Setup

1. Create a virtual environment and activate it.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create a local env file:

```bash
cp .env.example .env
```

4. Set required values in `.env` as needed for your environment.

## Run Locally

From the `backend/` directory:

```bash
python manage.py runserver 0.0.0.0:8000
```

## Current Stub Endpoints

- `POST /api/auth/register`
- `POST /api/auth/login`
- `POST /api/auth/firebase-login`
- `GET /api/roadmaps`
- `POST /api/roadmaps`

## Firebase Stub Fallback Behavior

- Setting: `AUTH_STUB_ALLOW_FIREBASE_FALLBACK`
- If this variable is unset, fallback defaults to the value of `DJANGO_DEBUG`.
- Recommended values:
	- Local development: `true`
	- Non-dev environments: `false`

When fallback is disabled and token verification fails, `POST /api/auth/firebase-login` returns `401`.

## Validation Commands

Run system checks:

```bash
python manage.py check
```

Run tests (preferred for Django test client coverage):

```bash
python manage.py test tests -v 2
```
