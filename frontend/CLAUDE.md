@AGENTS.md

# NidhiFlow AI — Frontend

This is the Next.js frontend for **NidhiFlow AI – Enterprise Agentic Loan Operations Platform**. It deploys to Vercel and will talk to a FastAPI backend (not built yet) over HTTPS at `/api`.

**Live deployment:** https://nidhiflow-ai.vercel.app/

For project-wide context (architecture, current phase, roadmap), see the root `CLAUDE.md` and `../phase.txt` — this file intentionally does not duplicate that content. Check `phase.txt` before assuming a step (Firebase, backend, Docker, etc.) is ready to use.

## Stack already installed here

Next.js 16.2.10, React 19.2.4, Tailwind CSS v4, `@tanstack/react-query`, `react-hook-form` + `@hookform/resolvers` + `zod`, `framer-motion`, `recharts`, `sonner`, `next-themes`, `lucide-react`. Don't suggest re-installing or swapping these — check `package.json` before adding a new library that overlaps.

## Phase discipline

We are in Phase 2 (`../phase2.txt`). Step 1 (loan-application intake page, dashboard) is complete. Step 2 (real document upload via Firebase Storage, in `loan-application/document-upload-section.tsx`) is complete. Steps 3-8 (backend: LangGraph pipeline, Sarvam OCR, Gemma validation, orchestrator, monitoring, reporting) are complete — backend only, see `../backend/CLAUDE.md`. Step 8b (frontend) is in progress: the loan detail & timeline page (`app/dashboard/loan/[id]/`) is done; human review queue, audit trail viewer, and monitoring dashboard upgrade are still pending. Do not add Docker files until `../phase2.txt` marks the corresponding step as done.

## Routing conventions established in Step 8b

- Per-loan/detail pages that need the dashboard's auth-gated nav shell go under `app/dashboard/<route>/`, not top-level `app/<route>/` — `app/dashboard/layout.tsx` is a Client Component that redirects to `/auth` if unauthenticated and wraps children in `DashboardShell`.
- New data-fetching pages default to async Server Components (`await params`, direct `fetch` in the component) rather than client-side `useEffect`/`useState` — this Next.js version's modern pattern per `AGENTS.md`. The existing `app/dashboard/page.tsx` is still a Client Component (pre-dates this decision) — don't treat it as the pattern to copy for new pages.
- Dynamic route error/not-found handling: `not-found.tsx` (Server Component, triggered by `notFound()`) and `error.tsx` (must be `"use client"`, receives `{ error, unstable_retry }` in this Next.js version — not the older `reset` prop) live alongside `page.tsx` in the same route segment.
- Shared status-chip colors live in `lib/status-styles.ts` (`getStatusChipStyle`) and currency formatting in `lib/format.ts` (`formatCurrency`) — both were previously duplicated per-component; extend these instead of re-inlining.
