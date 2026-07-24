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
app/agents/    Phase 2 Step 5: StateGraph (graph.py, nodes.py) + document_intelligence/ (Sarvam Vision OCR) + validation_compliance/ (Sarvam-105B field extraction: sarvam_chat_client.py, prompts.py, schemas.py, agent.py — deterministic cross-checks in agent.py, no LLM for comparisons) — no conditional routing/checkpointer yet
app/utils/     shared helpers
```

## Database & migrations

SQLAlchemy engine/session/`Base`/`get_db()` live in `app/core/database.py`. Schema migrations are managed with Alembic (`backend/alembic/`), not `Base.metadata.create_all()`. After pulling new migrations: `uv run alembic upgrade head` (Cloud SQL Auth Proxy must already be running — see below). To generate a new migration after changing models: `uv run alembic revision --autogenerate -m "<description>"`, then review the diff before applying.

## Local Cloud SQL access

Local dev DB access goes through the Cloud SQL Auth Proxy on `127.0.0.1:5432` — nothing connects directly. Run `cloud-sql-proxy.exe <instance-connection-name> --port=5432 --gcloud-auth` before any DB-touching code (incl. `/health/db`) will work. `--gcloud-auth` is needed unless Application Default Credentials are set up.

If the backend is already running, both `uv run alembic upgrade head` and `uv run alembic revision --autogenerate` fail with `Access is denied` (venv is locked) — use `./.venv/Scripts/python.exe -m alembic ...` directly instead, then manually restart uvicorn (see reload gotcha below).

Don't echo raw exception text from DB/infra errors into HTTP responses (can leak DSN/credentials) — log server-side via `logging`, return a generic client-facing message.

## Dev server reload gotcha

`uvicorn --reload`'s file-watcher here does not reliably pick up edits to `app/models/` or `app/schemas/` — confirmed twice (new columns/fields silently missing from API responses after editing). After any model/schema change, manually restart: find the python PIDs (`Get-Process python`), kill them, then re-run `uv run uvicorn main:app --reload`. Don't trust a live API test after such an edit without doing this first.

If `uv run <cmd>` fails with `Access is denied` on a `.venv/Lib/site-packages/...` file, the running server has it locked — use `./.venv/Scripts/python.exe -m <module>` (e.g. `-m alembic ...`, `-m pytest -q`) directly instead, which skips `uv sync`.

## Phase discipline

We are in Phase 2 (`../phase2.txt`). Step 1 (loan/customer/document models + CRUD) is complete. Step 2 (document upload, intake submit, LangGraph state) is complete. Step 3 (minimal `StateGraph`) is complete. Step 4 (real Document Intelligence agent: Sarvam Vision OCR, `document_ocr_results` table) is complete. Step 5 (Validation & Compliance agent: Sarvam-105B field extraction + deterministic cross-checks, `document_validation_results` + `loan_validation_summaries` tables) is complete. Step 6 (Pipeline Orchestrator: deterministic decision engine in `app/agents/pipeline_orchestrator/`, `workflow_executions`/`workflow_events` tables, `submit_loan_application()` now advances `loan.status` to `Processing` or `Human Review` based on the orchestrator's decision) is complete — backend only, frontend Pipeline Status panel deferred. Step 7 (Monitoring & Self-Healing: Postgres-backed LangGraph checkpointing via `langgraph-checkpoint-postgres`, per-node telemetry via `app/agents/monitoring/track_node` decorator + `node_executions` table, a bounded self-healing retry loop in `run_loan_workflow_with_recovery()`, and a read-only `GET /monitoring/health` endpoint) is complete. Graph is still linear (no conditional routing, no interrupts) — that's intentional per `../phase2.txt`; the checkpointer gives durability/audit, not skip-ahead resume, since there's no pause point yet. No Docker until `../phase2.txt` marks the corresponding step as done.

The compiled `loan_workflow_graph` (in `app/agents/graph.py`) now holds a live psycopg v3 connection pool for its Postgres checkpointer — the Cloud SQL Auth Proxy must be running before importing `app.agents.graph` or anything that imports it (this was already true for the rest of the backend, so it's not a new constraint in practice).

Step 8 (Reporting & Audit Dashboard, backend only — `app/services/reporting_service.py` + `app/api/reporting.py`, prefix `/reporting`: per-loan merged timeline, paginated global audit trail, retry analytics, human-review analytics, per-status processing-timeline breakdown) is complete. Deliberately does not duplicate `GET /monitoring/health` (Step 7, node health/failure stats) or `GET /dashboard/stats` (coarse loan-count KPIs) — see `phase2.txt` for the exact overlap reasoning. `GET /reporting/loans/{id}/timeline` was extended during Step 8b to also return `loan`/`customer`/`validation_summary` alongside `events`, so the frontend detail page is a single fetch.

Step 8b (frontend, in progress) has the loan detail & timeline page done (`frontend/src/app/dashboard/loan/[id]/`); human review queue, audit trail viewer, and monitoring dashboard upgrade are still pending.

Backend auth exists: `app/core/firebase_auth.py` verifies Firebase ID tokens (`get_current_firebase_user`) and enforces per-user ownership (`require_owned_customer_id`, `require_owned_loan`) on customer/loan/document routes. `Customer.firebase_uid` links a DB row to the Firebase user. `/reporting/*` (except the PDF report route) and `GET /loan/{id}` are still anonymous — extend the same dependency if protecting them later.

## Firebase Admin: single shared init

`firebase_admin.initialize_app()` can only run once per process (default app) — calling it from a second module throws `ValueError: The default Firebase app already exists`, and this exact bug once made OCR crash with a misleading `OCR_ERROR`. Any code needing Firebase Admin (Storage, Auth token verification, etc.) must call `app.core.firebase_app.get_firebase_app()` rather than initializing its own app.

## Native Postgres enum columns store the Python member NAME, not `.value`

`sa.Enum(SomeEnum, name="...")` binds using the enum member's `.name` (e.g. `SALE_AGREEMENT`), not its `.value` string (e.g. `"Sale Agreement"`) — confirmed the hard way when a migration added new `DocumentType` labels using `.value` strings and every insert of a new type failed. Alembic autogenerate does not detect new enum members at all; add them by hand: `op.execute("ALTER TYPE <enum_name> ADD VALUE IF NOT EXISTS '<MEMBER_NAME>'")`, using the member name.

PDF generation uses `reportlab` (Platypus), not WeasyPrint/xhtml2pdf — those need GTK/Pango system libraries that are painful to install on Windows dev machines. `app/services/report_service.py` is the pattern to follow for new PDF reports.

Sarvam OCR reads uploaded documents from Firebase Storage via `firebase-admin` + `credentials.ApplicationDefault()` (uses this machine's local gcloud ADC login — will need a service-account key once the backend is actually deployed). `SARVAM_API_KEY`/`GEMINI_API_KEY` blank-default means the corresponding node skips gracefully (status `"skipped"`) rather than erroring when unset.

Step 5 uses **Sarvam-105B** (`sarvam_chat_client.py`, OpenAI-compatible `POST {SARVAM_BASE_URL}/v1/chat/completions`, reusing `SARVAM_API_KEY`/`SARVAM_BASE_URL`) — migrated off Gemma-4/`google-genai` after live-testing showed Sarvam-105B is purpose-built for this exact Indian-KYC-document pipeline shape and doesn't hit the free-tier 429s Gemini did under concurrent document validation. `SARVAM_CHAT_MODEL` is env-overridable. **Use `"response_format": {"type": "json_object"}`, not `{"type": "json_schema", "strict": true}`** — live-tested both, and strict schema mode reliably nulled out `detected_document_type` (the type-mismatch signal) even when the model clearly reasoned about it in `notes`; plain `json_object` mode gets the same fields filled correctly. Extraction (semantic understanding) uses the LLM; cross-document comparison (PAN/Aadhaar consistency, EMI-vs-income) is deterministic Python in `validation_compliance/agent.py`, not a second LLM call.

## No test suite yet

`backend/tests/` doesn't exist. Verify agent/pipeline changes end-to-end by scripting a direct call: `./.venv/Scripts/python.exe -c "..."` — create `Customer`/`LoanApplication` rows via the SQLAlchemy models, call `submit_loan_application(db, loan, LoanApplicationSubmit(changed_by=...))` directly (runs the real LangGraph pipeline, no mocking), inspect the result/generated PDF, then delete the test rows.

## Sarvam Doc Digitization API has no prompt parameter

`document_intelligence`'s Sarvam job API (`app/agents/document_intelligence/sarvam_client.py`) only accepts `language`/`output_format` in `job_parameters` — confirmed against Sarvam's own docs, there is no prompt/instruction field on this endpoint. Sarvam's separate "Extract" product does take a prompt, but don't add it here — it would duplicate `validation_compliance`'s Sarvam-105B-based extraction. Sarvam also supports ZIP multi-file batching per job (unused here — each document still gets its own job; concurrency is handled via a `ThreadPoolExecutor` in `agent.py` instead, batching was deliberately deferred).

## Required-field policies (loan intake)

Required *document* types per loan type live in `app/core/document_checklist.py::REQUIRED_DOCUMENT_TYPES` (use the shared `compute_missing_required_documents()` helper, don't reinline). Required *form* fields per loan type (a policy that didn't exist before — nothing previously enforced loan-type-specific fields like `gst_number`/`property_value` anywhere, frontend or backend) live in `app/agents/intake_supervisor/agent.py::REQUIRED_FORM_FIELDS_BY_LOAN_TYPE`.

## `app/utils/` shared helpers

- `http_retry.py::request_with_retry()` — exponential-backoff HTTP retry (429/5xx + timeouts), used by both `document_intelligence/sarvam_client.py` (Vision OCR) and `validation_compliance/sarvam_chat_client.py` (chat completions) so the two Sarvam clients don't duplicate retry logic.
- `friendly_messages.py::friendly_decision_message()` / `friendly_workflow_event_description()` — turns the raw `event_type`/`message` strings that `pipeline_orchestrator/decision_engine.py::build_audit_trail()` writes to `workflow_events` (e.g. `"validation_compliance status=failed confidence=0.9"`) into human-facing text, without touching the stored row. Lives here specifically so both `report_service.py` (PDF) and `reporting_service.py` (`GET /reporting/loans/{id}/timeline`, which feeds the frontend Loan Timeline panel) can import it — putting it in either service module directly would create a circular import between the two.

## PAN/Aadhaar comparisons need whitespace-stripped normalization, not name-style normalization

`validation_compliance/agent.py::_normalize()` (lowercase + collapse repeated whitespace) is correct for **names** but wrong for **ID numbers** — a real Aadhaar card prints the number spaced (`"1234 5678 9012"`) while the application record stores it digit-only, so `_normalize()` alone left them unequal and produced a false "Aadhaar Number Matches Application Record: No". Fixed by adding `_normalize_id()` (strips whitespace entirely) and using it for the PAN/Aadhaar-vs-customer-record comparisons in both `agent.py` and `report_service.py::_build_verification_checklist` — keep using `_normalize()` for name fields, `_normalize_id()` for any ID/number field.

## PDF report includes a non-decision "AI Operations Summary"

`report_service.py::build_loan_report_pdf()` renders an "AI Operations Summary" section (customer greeting, a few positive highlights derived from the checklist, and an "Indicative application strength" percentage) computed deterministically from the same checklist/summary data as the rest of the report — no extra LLM call. The percentage is explicitly labeled as an automated estimate, not a sanction/offer/guarantee, per this project's compliance rule that AI never makes the lending decision. Don't let this section imply otherwise when extending it.
