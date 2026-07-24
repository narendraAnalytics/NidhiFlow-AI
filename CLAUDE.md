# NidhiFlow AI

Enterprise Agentic Loan Operations Platform. AI automates loan **operations** (document intake, validation, pipelines, monitoring, audit) for Home/Personal/Business Loans — it never makes the lending decision; that stays with human underwriters.

## Source of truth

- `workflow.txt` — full architecture discussion and 6-phase roadmap. Read for the "why" behind any structural decision.
- `phase.txt` — **live tracker**. Always check this before acting: what's done, what step is next, what's explicitly out of scope right now. Update its checkboxes as steps complete.

## Phase discipline

We build incrementally. Do not introduce Docker, LangGraph/AI agents, Kubernetes, GitHub Actions/CI-CD, or Prometheus/Grafana until `phase.txt` marks that phase as active. Phase 1 is foundation only (Next.js, FastAPI, PostgreSQL, Firebase Auth/Storage) — no business logic, no agents.

## Sequencing rule

Google Cloud CLI and Firebase MCP setup happen one step at a time, as separately approved actions — never bundle multiple infra setup steps into one turn.

## Compliance phrasing

Never describe the platform as "RBI compliant." Always phrase it as "designed using principles from the RBI Digital Lending Directions, 2025."

## Deployment

Frontend is live on Vercel: https://nidhiflow-ai.vercel.app/ (deployed manually by the user; not automated via CI/CD — see phase discipline above). Backend has no deployment yet — still local-only (`localhost:8000`).

## Subprojects

- `frontend/` has its own `CLAUDE.md` (which imports `AGENTS.md`) with Next.js-version-specific rules — this installed Next.js version has breaking changes vs. typical training data, so check `frontend/node_modules/next/dist/docs/` before writing App Router or config code there. Those rules apply in addition to this file.
- `backend/` has its own `CLAUDE.md` with FastAPI/uv-specific conventions. Those rules apply in addition to this file.

## Infra gotchas (Firebase MCP / gcloud)

- To restart the backend cleanly after editing multiple files under `backend/app/agents/` or `backend/app/services/`: `powershell -Command "Get-Process python | Select-Object Id,ProcessName"`, then `Stop-Process -Id <reloader-pid>,<server-pid> -Force`, then re-run `uv run uvicorn main:app --reload`. `--reload`'s file-watcher can coalesce several rapid edits into one silent reload — don't trust it after a multi-file change without this. A background-task notification reporting "failed with exit code 127" right after you intentionally `Stop-Process`'d it is expected, not a bug.
- If the frontend shows "Failed to load dashboard data" or any API call fails, check first whether `cloud-sql-proxy.exe` and the backend (`uv run uvicorn main:app --reload`) are actually running — both are required locally and neither auto-starts. This was the root cause the one time it came up, not an app bug.
- `cloud-sql-proxy.exe` is already installed at `C:\Users\ES\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin\cloud-sql-proxy.exe` — no need to search for it or reinstall in a fresh session. Start it with:
  `"C:\Users\ES\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin\cloud-sql-proxy.exe" nidhiflow-ai-platform:asia-south1:nidhiflow-db-dev --port=5432 --gcloud-auth`
- `firebase_init` for the `storage` feature is unreliable — it can report success while writing nothing and never provisioning the bucket. Verify with `gcloud storage buckets list --project=<id>`; if empty, create the bucket via Firebase Console, then hand-write `firebase.json`/`storage.rules` and deploy with `firebase_deploy`.
- The Firebase MCP session caches project state (e.g. billing plan). If a value you just changed in the console (like a Blaze upgrade) doesn't show up in `firebase_get_environment`, reconnect via `/mcp` before retrying.
- New GCP projects default Cloud SQL to "Enterprise Plus" edition, which rejects shared-core tiers like `db-f1-micro`. Pass `--edition=ENTERPRISE` explicitly for cost-sensitive dev instances.
- Application Default Credentials (`gcloud auth application-default login`) aren't set up by default and require an interactive browser login — hand this to the user via `! <command>`, don't try to run it yourself.
- If Firebase Auth (e.g. Google popup sign-in) fails in a real Chrome profile but works fine in Incognito, the real bug is usually already fixed server-side (unauthorized domain, COOP headers, etc.) — the profile itself is just wedged with stale cookies/localStorage/IndexedDB/service-worker state from earlier broken attempts. Fix: `chrome://settings/content/all` → search the domain → **Clear data** → retry in a fresh tab.

## Git structure

This root directory is a single git repository covering both `frontend/` and `backend/` (remote: `github.com/narendraAnalytics/NidhiFlow-AI`). Run git commands from root, not from inside the subprojects. `phase.txt` and `workflow.txt` are intentionally gitignored — they're live planning docs, not shipped code.
