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
app/agents/    Phase 2 Step 5: StateGraph (graph.py, nodes.py) + document_intelligence/ (Sarvam Vision OCR) + validation_compliance/ (Gemma 4 field extraction: gemini_client.py, prompts.py, schemas.py, agent.py — deterministic cross-checks in agent.py, no LLM for comparisons) — no conditional routing/checkpointer yet
app/utils/     shared helpers
```

## Database & migrations

SQLAlchemy engine/session/`Base`/`get_db()` live in `app/core/database.py`. Schema migrations are managed with Alembic (`backend/alembic/`), not `Base.metadata.create_all()`. After pulling new migrations: `uv run alembic upgrade head` (Cloud SQL Auth Proxy must already be running — see below). To generate a new migration after changing models: `uv run alembic revision --autogenerate -m "<description>"`, then review the diff before applying.

## Local Cloud SQL access

Local dev DB access goes through the Cloud SQL Auth Proxy on `127.0.0.1:5432` — nothing connects directly. Run `cloud-sql-proxy.exe <instance-connection-name> --port=5432 --gcloud-auth` before any DB-touching code (incl. `/health/db`) will work. `--gcloud-auth` is needed unless Application Default Credentials are set up.

Don't echo raw exception text from DB/infra errors into HTTP responses (can leak DSN/credentials) — log server-side via `logging`, return a generic client-facing message.

## Phase discipline

We are in Phase 2 (`../phase2.txt`). Step 1 (loan/customer/document models + CRUD) is complete. Step 2 (document upload, intake submit, LangGraph state) is complete. Step 3 (minimal `StateGraph`) is complete. Step 4 (real Document Intelligence agent: Sarvam Vision OCR, `document_ocr_results` table) is complete. Step 5 (Validation & Compliance agent: Gemma 4 field extraction + deterministic cross-checks, `document_validation_results` + `loan_validation_summaries` tables) is complete. Step 6 (Pipeline Orchestrator: deterministic decision engine in `app/agents/pipeline_orchestrator/`, `workflow_executions`/`workflow_events` tables, `submit_loan_application()` now advances `loan.status` to `Processing` or `Human Review` based on the orchestrator's decision) is complete — backend only, frontend Pipeline Status panel deferred. Step 7 (Monitoring & Self-Healing: Postgres-backed LangGraph checkpointing via `langgraph-checkpoint-postgres`, per-node telemetry via `app/agents/monitoring/track_node` decorator + `node_executions` table, a bounded self-healing retry loop in `run_loan_workflow_with_recovery()`, and a read-only `GET /monitoring/health` endpoint) is complete. Graph is still linear (no conditional routing, no interrupts) — that's intentional per `../phase2.txt`; the checkpointer gives durability/audit, not skip-ahead resume, since there's no pause point yet. No Docker until `../phase2.txt` marks the corresponding step as done.

The compiled `loan_workflow_graph` (in `app/agents/graph.py`) now holds a live psycopg v3 connection pool for its Postgres checkpointer — the Cloud SQL Auth Proxy must be running before importing `app.agents.graph` or anything that imports it (this was already true for the rest of the backend, so it's not a new constraint in practice).

Step 8 (Reporting & Audit Dashboard, backend only — `app/services/reporting_service.py` + `app/api/reporting.py`, prefix `/reporting`: per-loan merged timeline, paginated global audit trail, retry analytics, human-review analytics, per-status processing-timeline breakdown) is complete. Deliberately does not duplicate `GET /monitoring/health` (Step 7, node health/failure stats) or `GET /dashboard/stats` (coarse loan-count KPIs) — see `phase2.txt` for the exact overlap reasoning. `GET /reporting/loans/{id}/timeline` was extended during Step 8b to also return `loan`/`customer`/`validation_summary` alongside `events`, so the frontend detail page is a single fetch.

Step 8b (frontend, in progress) has the loan detail & timeline page done (`frontend/src/app/dashboard/loan/[id]/`); human review queue, audit trail viewer, and monitoring dashboard upgrade are still pending.

**Known backlog item:** no endpoint in `app/api/` has authentication (confirmed via grep — zero `Depends(get_current_user)` or equivalent anywhere in the backend). Flagged by an automated security review during Step 8b; user explicitly decided to track as backlog rather than block feature work. `/reporting/*` in particular returns customer names and audit notes with no access control. Needs a real fix (Firebase ID token verification dependency, scoped queries) before any real deployment.

Sarvam OCR reads uploaded documents from Firebase Storage via `firebase-admin` + `credentials.ApplicationDefault()` (uses this machine's local gcloud ADC login — will need a service-account key once the backend is actually deployed). `SARVAM_API_KEY`/`GEMINI_API_KEY` blank-default means the corresponding node skips gracefully (status `"skipped"`) rather than erroring when unset.

Step 5 uses **Gemma 4** (`gemma-4-26b-a4b-it`) via the `google-genai` SDK, not Gemini — confirmed working with `response_schema` structured JSON output against this project's actual free-tier `GEMINI_API_KEY` (live-tested, not just documented). `GEMINI_MODEL` is env-overridable to swap to a Gemini model (e.g. `gemini-3.5-flash-lite`) if needed later. Extraction (semantic understanding) uses the LLM; cross-document comparison (PAN/Aadhaar consistency, EMI-vs-income) is deterministic Python in `validation_compliance/agent.py`, not a second LLM call.
