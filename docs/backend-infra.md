# Backend Infrastructure Notes

## Supabase Connection

- Use Supabase Postgres as the primary database for Django.
- Connect via standard Postgres connection string or discrete settings.
- Require SSL in production (`sslmode=require`).

Example env var pattern (preferred):

```
DATABASE_URL=postgresql://<user>:<password>@<host>:<port>/<db>?sslmode=require
```

Alternate discrete vars:

```
DB_NAME=
DB_USER=
DB_PASSWORD=
DB_HOST=
DB_PORT=
DB_SSLMODE=require
```

## Django Settings

- Prefer `DATABASE_URL` with `dj-database-url` for single-source configuration.
- Ensure connection pooling is enabled if using Supabase pooler (recommended for serverless deployments).
- Keep DB credentials in environment variables only.

## Migrations

- Use standard Django migrations.
- Run migrations against Supabase Postgres the same way as local Postgres.

Common commands:

```
python manage.py makemigrations
python manage.py migrate
```

## Local Development

- Use a local Postgres instance or Supabase local dev stack.
- When using Supabase local:
  - Set `DATABASE_URL` to the local Supabase Postgres.
  - Keep schema in sync via Django migrations, not direct SQL edits.

## Environment Variables

Required (minimum):

```
DATABASE_URL=
SUPABASE_URL=
SUPABASE_SERVICE_ROLE_KEY=
DJANGO_SECRET_KEY=
OPENROUTER_API_KEY=
```

Optional:

```
DB_SSLMODE=require
```

Notes:

- `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` are needed for any direct Supabase API usage (if used).
- `OPENROUTER_API_KEY` is required for the agentic skill runner (`backend/agent/runner.py`). Skills call Gemini via OpenRouter.
- Avoid exposing service role keys or the OpenRouter API key in the client.
