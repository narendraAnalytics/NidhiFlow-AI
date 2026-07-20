# NidhiFlow AI

**Enterprise Agentic Loan Operations Platform**
*Transforming Loan Operations with Intelligent Automation*

NidhiFlow AI automates and orchestrates the operational lifecycle of Home, Personal, and Business Loans for banks and NBFCs — document intake, validation, data pipelines, monitoring, and audit reporting — while keeping the final lending decision with human underwriters. AI accelerates **operations**, not approval.

Full architecture discussion: [`workflow.txt`](./workflow.txt).
Live Phase 1 checklist: [`phase.txt`](./phase.txt).

## Architecture

```text
                    Users
                      │
                      ▼
         ┌────────────────────────┐
         │   Vercel (Next.js)      │
         │      Frontend UI        │
         └──────────┬──────────────┘
                    │ HTTPS
                    ▼
         ┌────────────────────────┐
         │ Google Cloud Platform   │
         │                        │
         │ FastAPI + LangGraph    │
         │ AI Agents             │
         └──────────┬─────────────┘
                    │
        ┌───────────┼─────────────┐
        ▼           ▼             ▼
   Cloud SQL   Firebase      GCS Bucket
  PostgreSQL    Auth/Storage  Documents
                    │
                    ▼
          Prometheus + Grafana
```

Five agents sit behind a Supervisor: **Intake & Document Intelligence**, **Validation & Compliance**, **Pipeline Orchestrator**, **Monitoring & Self-Healing**, and **Reporting & Audit**. Loan-product rules (Home / Personal / Business) live in a configurable rules engine, not hardcoded logic. Low-confidence validations route to a Human Review Queue.

The platform is designed using principles from the RBI Digital Lending Directions, 2025 (KFS disclosure, borrower consent audit trails, grievance redressal) — it is not claimed to be RBI compliant.

## Repository layout

```
frontend/     Next.js frontend (Vercel)
backend/      FastAPI backend (planned — Phase 1)
docs/         Project documentation (planned — Phase 1)
phase.txt     Live Phase 1 tracker — current step, what's done, what's next
workflow.txt  Full architecture & roadmap discussion (source doc)
```

## Status

**Phase 1 — Foundation**, in progress. See [`phase.txt`](./phase.txt) for the live checklist of what's done and what's next.

## Getting started

```bash
cd frontend
npm run dev
```

Open [http://localhost:3000](http://localhost:3000). The backend does not exist yet — see `phase.txt` Step B.

## Roadmap

1. **Foundation** — Next.js, FastAPI, PostgreSQL, Firebase *(current)*
2. **Loan workflow** — LangGraph, five AI agents
3. **Docker** + Docker Compose
4. **GitHub Actions** + Artifact Registry
5. **Google Kubernetes Engine** deployment
6. **Prometheus, Grafana**, autoscaling, production hardening
