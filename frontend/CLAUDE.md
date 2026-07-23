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

## Loan application form pattern

`loan-application/page.tsx` handles Home/Personal/Business loan types with **one flat Zod schema** (all type-specific fields optional) plus inline `{isHome/isPersonal/isBusiness && (...)}` JSX blocks keyed off `watch("loan_type")` — not separate sub-components or a config-driven field list. Follow this pattern for new fields/loan types rather than introducing a new structure. Shared PAN/Aadhaar/ID-format validators live in `lib/validators.ts` — extend that instead of inlining regex/checksum logic in a form. To live-transform an input as the user types (e.g. force-uppercase), pass `onChange` inside `register(name, { onChange: (e) => { e.target.value = ... } })` — react-hook-form picks up the mutated value.

## Shared loan-result components

Shared loan-result UI (validation summary card, agent pipeline stepper, timeline, PDF download button) lives in `components/loan/` (`loan-summary-card.tsx`, `agent-pipeline.tsx`, `loan-timeline.tsx`, `download-report-button.tsx`) — reused by both `app/dashboard/loan/[id]/page.tsx` and the inline "done" step of `app/loan-application/page.tsx`. Extend these rather than re-inlining when showing loan results elsewhere.

## Design tokens (light theme, established across dashboard-shell/topbar/sidebar/kpi-card)

Reuse rather than reinvent: page bg `bg-[#f8fbff]` + blurred decorative blobs; cards `rounded-[24-28px] border border-white/60 bg-white/75 shadow-[0_8px_30px_rgba(15,27,51,0.06)] backdrop-blur-xl`; primary CTA gradient `from-[#26D9FF] via-[#3B82F6] to-[#A855F7]`; heading text `text-[#0f1b33]`, muted text `text-[#5b6b8c]`. The real brand logo is a Cloudinary PNG at the `LOGO_URL` const in `components/landing/navbar.tsx` (not a generated mark) — reuse that URL with `next/image` + `unoptimized` for any other page needing it.

## Known noisy diagnostics (safe to ignore)

- Tailwind v4 "canonical class" suggestions (e.g. `bg-gradient-to-r` → `bg-linear-to-r`) are cosmetic; the codebase consistently uses the `bg-gradient-to-*` form already — don't convert.
- `npx tsc --noEmit` can transiently fail on `.next/dev/types/validator.ts` / `.next/types/validator.ts` right after a dev-server file save (stale route-type regen) — rerun once before treating it as a real error.
