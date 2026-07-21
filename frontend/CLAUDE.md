@AGENTS.md

# NidhiFlow AI — Frontend

This is the Next.js frontend for **NidhiFlow AI – Enterprise Agentic Loan Operations Platform**. It deploys to Vercel and will talk to a FastAPI backend (not built yet) over HTTPS at `/api`.

**Live deployment:** https://nidhiflow-ai.vercel.app/

For project-wide context (architecture, current phase, roadmap), see the root `CLAUDE.md` and `../phase.txt` — this file intentionally does not duplicate that content. Check `phase.txt` before assuming a step (Firebase, backend, Docker, etc.) is ready to use.

## Stack already installed here

Next.js 16.2.10, React 19.2.4, Tailwind CSS v4, `@tanstack/react-query`, `react-hook-form` + `@hookform/resolvers` + `zod`, `framer-motion`, `recharts`, `sonner`, `next-themes`, `lucide-react`. Don't suggest re-installing or swapping these — check `package.json` before adding a new library that overlaps.

## Phase discipline

We are in Phase 2 (`../phase2.txt`). Step 1 (loan-application intake page, dashboard) is complete. Step 2 (real document upload via Firebase Storage, in `loan-application/document-upload-section.tsx`) is in progress. Do not add Docker files or agent-related UI until `../phase2.txt` marks the corresponding step as done.
