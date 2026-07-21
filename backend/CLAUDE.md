# NidhiFlow AI — Backend

FastAPI backend for **NidhiFlow AI – Enterprise Agentic Loan Operations Platform**. Runs locally on `localhost:8000`; the frontend calls it at `/api`.

For project-wide context (architecture, current phase, roadmap), see the root `CLAUDE.md` and `../phase.txt` — this file intentionally does not duplicate that content.

## Stack

Python 3.12, managed with **uv** (not pip/venv directly): `pyproject.toml` + `uv.lock` + `.venv`. FastAPI, `uvicorn[standard]`, `python-dotenv`.

- Add a dependency: `uv add <package>`
- Keep `requirements.txt` in sync after any dependency change: `uv export --no-hashes --format requirements-txt -o requirements.txt`
- Run the dev server: `uv run uvicorn main:app --reload`

## Layout

Layered architecture: FastAPI → Auth → API → Services → (future) AI Agents → Database.

```
app/api/       route handlers
app/core/      config, startup, cross-cutting concerns
app/models/    DB models
app/schemas/   pydantic schemas
app/services/  business logic
app/agents/    stays empty until Phase 2 — do not add logic yet
app/utils/     shared helpers
```

## Database & migrations

SQLAlchemy engine/session/`Base`/`get_db()` live in `app/core/database.py`. Schema migrations are managed with Alembic (`backend/alembic/`), not `Base.metadata.create_all()`. After pulling new migrations: `uv run alembic upgrade head` (Cloud SQL Auth Proxy must already be running — see below). To generate a new migration after changing models: `uv run alembic revision --autogenerate -m "<description>"`, then review the diff before applying.

## Local Cloud SQL access

Local dev DB access goes through the Cloud SQL Auth Proxy on `127.0.0.1:5432` — nothing connects directly. Run `cloud-sql-proxy.exe <instance-connection-name> --port=5432 --gcloud-auth` before any DB-touching code (incl. `/health/db`) will work. `--gcloud-auth` is needed unless Application Default Credentials are set up.

Don't echo raw exception text from DB/infra errors into HTTP responses (can leak DSN/credentials) — log server-side via `logging`, return a generic client-facing message.

## Phase discipline

We are in Phase 1 (foundation). No business logic, no LangGraph/AI agents, no Docker until `../phase.txt` marks the corresponding step as done.
