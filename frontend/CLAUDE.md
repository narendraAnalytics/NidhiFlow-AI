@AGENTS.md

# NidhiFlow AI — Frontend

This is the Next.js frontend for **NidhiFlow AI – Enterprise Agentic Loan Operations Platform**. It deploys to Vercel and will talk to a FastAPI backend (not built yet) over HTTPS at `/api`.

For project-wide context (architecture, current phase, roadmap), see the root `CLAUDE.md` and `../phase.txt` — this file intentionally does not duplicate that content. Check `phase.txt` before assuming a step (Firebase, backend, Docker, etc.) is ready to use.

## Stack already installed here

Next.js 16.2.10, React 19.2.4, Tailwind CSS v4, `@tanstack/react-query`, `react-hook-form` + `@hookform/resolvers` + `zod`, `framer-motion`, `recharts`, `sonner`, `next-themes`, `lucide-react`. Don't suggest re-installing or swapping these — check `package.json` before adding a new library that overlaps.

## Phase discipline

We are in Phase 1 (foundation). Do not add Firebase SDK calls, Docker files, or agent-related UI until `../phase.txt` marks the corresponding step as done.
