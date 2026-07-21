import { Activity, FileSearch, Network, ShieldCheck, Sparkles } from "lucide-react";
import { PreviewBadge } from "./preview-badge";
import { Sparkline } from "./sparkline";

const AGENTS = [
  {
    name: "Document Intelligence",
    description: "OCR & Document Processing",
    icon: FileSearch,
    color: "#22C55E",
    processed: 1284,
    successRate: 98.6,
    trend: [4, 6, 5, 8, 7, 9, 8],
  },
  {
    name: "Validation & Compliance",
    description: "Validation & Rule Checking",
    icon: ShieldCheck,
    color: "#F59E0B",
    processed: 1261,
    successRate: 97.8,
    trend: [3, 5, 4, 6, 5, 7, 6],
  },
  {
    name: "Pipeline Orchestrator",
    description: "Workflow & Orchestration",
    icon: Network,
    color: "#A855F7",
    processed: 1284,
    successRate: 99.1,
    trend: [5, 4, 6, 5, 7, 6, 8],
  },
  {
    name: "Monitoring & Self-Healing",
    description: "System Monitoring",
    icon: Activity,
    color: "#EC4899",
    processed: 124,
    successRate: 99.5,
    trend: [2, 3, 2, 4, 3, 5, 4],
  },
  {
    name: "Reporting & Audit",
    description: "Reports & Audit Trail",
    icon: Sparkles,
    color: "#3B82F6",
    processed: 342,
    successRate: 98.3,
    trend: [6, 5, 7, 6, 8, 7, 9],
  },
];

export function AiAgentPanel() {
  return (
    <div className="rounded-[28px] border border-white/60 bg-white/75 p-6 shadow-[0_8px_30px_rgba(15,27,51,0.06)] backdrop-blur-xl">
      <div className="mb-5 flex items-center justify-between">
        <h2 className="text-[16px] font-bold text-[#0f1b33]">AI Agent Performance</h2>
        <PreviewBadge />
      </div>

      <div className="flex flex-col gap-4">
        {AGENTS.map((agent) => (
          <div key={agent.name} className="flex items-center gap-3">
            <div
              className="flex h-10 w-10 shrink-0 items-center justify-center rounded-2xl"
              style={{ backgroundColor: `${agent.color}1A`, color: agent.color }}
            >
              <agent.icon size={18} />
            </div>
            <div className="min-w-0 flex-1">
              <div className="flex items-center gap-1.5">
                <span className="truncate text-[13.5px] font-bold text-[#0f1b33]">
                  {agent.name}
                </span>
                <span className="inline-flex h-1.5 w-1.5 shrink-0 rounded-full bg-[#22C55E]" />
              </div>
              <p className="truncate text-[11.5px] text-[#5b6b8c]">{agent.description}</p>
            </div>
            <div className="hidden w-16 shrink-0 sm:block">
              <Sparkline data={agent.trend} color={agent.color} />
            </div>
            <div className="shrink-0 text-right">
              <div className="text-[13px] font-bold text-[#0f1b33]">{agent.processed}</div>
              <div className="text-[11px] font-semibold text-[#15803d]">
                {agent.successRate}%
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
