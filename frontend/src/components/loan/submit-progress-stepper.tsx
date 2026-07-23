"use client";

import { useEffect, useState } from "react";
import {
  AlertTriangle,
  CheckCircle2,
  ClipboardCheck,
  GitBranch,
  Loader2,
  ScanText,
  ShieldCheck,
  type LucideIcon,
} from "lucide-react";

const STAGES: { label: string; icon: LucideIcon }[] = [
  { label: "Intake Supervisor", icon: ClipboardCheck },
  { label: "Document Intelligence (OCR)", icon: ScanText },
  { label: "Validation & Compliance", icon: ShieldCheck },
  { label: "Pipeline Orchestrator", icon: GitBranch },
];

const STAGE_INTERVAL_MS = 1200;

export type SubmitOutcome = "processing" | "human_review" | "failed" | null;

export function SubmitProgressStepper({ outcome }: { outcome: SubmitOutcome }) {
  const [activeIndex, setActiveIndex] = useState(0);

  useEffect(() => {
    if (outcome !== null) return;
    setActiveIndex(0);
    const interval = setInterval(() => {
      setActiveIndex((i) => (i < STAGES.length - 1 ? i + 1 : i));
    }, STAGE_INTERVAL_MS);
    return () => clearInterval(interval);
  }, [outcome]);

  const settled = outcome !== null;

  return (
    <div className="rounded-2xl border border-[#e2e8f5] bg-[#f8fbff]/60 p-5">
      <p className="mb-4 text-[13px] font-bold text-[#0f1b33]">
        {outcome === null && "Running the agent pipeline…"}
        {outcome === "processing" && "All checks passed — moving to processing."}
        {outcome === "human_review" && "Flagged for human review — a reviewer will take a look."}
        {outcome === "failed" && "Something went wrong submitting the application."}
      </p>

      <div className="flex flex-col gap-3">
        {STAGES.map((stage, index) => {
          const Icon = stage.icon;
          const isCurrent = !settled && index === activeIndex;
          const isDone = settled ? outcome !== "failed" : index < activeIndex;
          const color = isDone ? "#22C55E" : isCurrent ? "#3B82F6" : "#9aa8c2";

          return (
            <div key={stage.label} className="flex items-center gap-3">
              <div
                className="flex h-8 w-8 shrink-0 items-center justify-center rounded-xl"
                style={{ backgroundColor: `${color}1A`, color }}
              >
                {isDone ? (
                  <CheckCircle2 size={16} />
                ) : isCurrent ? (
                  <Loader2 size={16} className="animate-spin" />
                ) : (
                  <Icon size={16} />
                )}
              </div>
              <span
                className={`text-[13px] font-semibold ${isDone || isCurrent ? "text-[#0f1b33]" : "text-[#9aa8c2]"}`}
              >
                {stage.label}
              </span>
            </div>
          );
        })}
      </div>

      {outcome === "human_review" && (
        <div className="mt-4 flex items-start gap-2 rounded-xl bg-[#A855F7]/10 p-3 text-[12.5px] font-semibold text-[#7e22ce]">
          <AlertTriangle size={15} className="mt-0.5 shrink-0" />
          One or more checks need a human reviewer before this application can proceed.
        </div>
      )}
    </div>
  );
}
