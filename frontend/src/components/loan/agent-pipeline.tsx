import { ClipboardCheck, GitBranch, ScanText, ShieldCheck, type LucideIcon } from "lucide-react";
import type { LoanTimelineEvent } from "@/types/reporting";

type StageStatus = "pending" | "completed" | "failed";

interface Stage {
  nodeName: string;
  label: string;
  icon: LucideIcon;
  color: string;
}

const STAGES: Stage[] = [
  { nodeName: "intake_supervisor", label: "Intake Supervisor", icon: ClipboardCheck, color: "#3B82F6" },
  { nodeName: "document_intelligence", label: "Document Intelligence (OCR)", icon: ScanText, color: "#A855F7" },
  { nodeName: "validation_compliance", label: "Validation & Compliance", icon: ShieldCheck, color: "#14B8A6" },
  { nodeName: "pipeline_orchestrator", label: "Pipeline Orchestrator", icon: GitBranch, color: "#F59E0B" },
];

interface NodeExecutionInfo {
  status: StageStatus;
  duration: number | null;
  errorCategory: string | null;
  retryAttempt: number;
}

function latestNodeExecutions(events: LoanTimelineEvent[]): Map<string, NodeExecutionInfo> {
  const byNode = new Map<string, NodeExecutionInfo>();

  for (const event of events) {
    if (event.category !== "node_execution") continue;
    const [nodeName, rawStatus] = event.title.split(": ");
    const retryAttempt = Number(event.metadata.retry_attempt ?? 0);
    const existing = byNode.get(nodeName);
    if (existing && existing.retryAttempt > retryAttempt) continue;

    byNode.set(nodeName, {
      status: rawStatus === "failed" ? "failed" : "completed",
      duration: typeof event.metadata.duration === "number" ? event.metadata.duration : null,
      errorCategory:
        typeof event.metadata.error_category === "string" ? event.metadata.error_category : null,
      retryAttempt,
    });
  }

  return byNode;
}

function formatDuration(seconds: number | null): string | null {
  if (seconds === null) return null;
  return seconds < 1 ? `${Math.round(seconds * 1000)}ms` : `${seconds.toFixed(1)}s`;
}

export function AgentPipeline({ events }: { events: LoanTimelineEvent[] }) {
  const executions = latestNodeExecutions(events);

  return (
    <div className="rounded-[28px] border border-white/60 bg-white/75 p-6 shadow-[0_8px_30px_rgba(15,27,51,0.06)] backdrop-blur-xl">
      <h2 className="mb-5 text-[16px] font-bold text-[#0f1b33]">Agent Pipeline</h2>

      <div className="flex flex-col gap-4 lg:flex-row lg:gap-3">
        {STAGES.map((stage, index) => {
          const info = executions.get(stage.nodeName);
          const status: StageStatus = info?.status ?? "pending";
          const Icon = stage.icon;
          const color = status === "failed" ? "#EC4899" : status === "pending" ? "#9aa8c2" : stage.color;
          const duration = formatDuration(info?.duration ?? null);

          return (
            <div key={stage.nodeName} className="flex flex-1 items-start gap-3 lg:flex-col lg:items-stretch">
              <div className="flex flex-col items-center lg:flex-row lg:items-center lg:gap-2">
                <div
                  className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl"
                  style={{ backgroundColor: `${color}1A`, color }}
                >
                  <Icon size={18} />
                </div>
                {index < STAGES.length - 1 && (
                  <div className="mt-1 w-px flex-1 bg-[#0f1b33]/10 lg:mt-0 lg:h-px lg:w-full lg:flex-1" />
                )}
              </div>
              <div className="min-w-0 flex-1 pb-2 lg:pb-0">
                <p className="text-[12.5px] font-bold text-[#0f1b33]">{stage.label}</p>
                <div className="mt-0.5 flex flex-wrap items-center gap-1.5">
                  <span
                    className="rounded-full px-2 py-0.5 text-[10.5px] font-bold uppercase tracking-wide"
                    style={{ backgroundColor: `${color}1A`, color }}
                  >
                    {status}
                  </span>
                  {duration && <span className="text-[11px] text-[#5b6b8c]">{duration}</span>}
                  {info?.retryAttempt ? (
                    <span className="text-[11px] text-[#5b6b8c]">retry {info.retryAttempt}</span>
                  ) : null}
                </div>
                {info?.errorCategory && (
                  <p className="mt-1 text-[11px] font-semibold text-[#be185d]">{info.errorCategory}</p>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
