import { Activity, CheckCircle2, History, XCircle } from "lucide-react";
import type { LoanTimelineEvent, TimelineEventCategory } from "@/types/reporting";

const CATEGORY_ICONS: Record<TimelineEventCategory, typeof History> = {
  status_change: History,
  workflow_event: Activity,
  node_execution: CheckCircle2,
};

const CATEGORY_COLORS: Record<TimelineEventCategory, string> = {
  status_change: "#3B82F6",
  workflow_event: "#A855F7",
  node_execution: "#22C55E",
};

function formatTimestamp(iso: string): string {
  return new Date(iso).toLocaleString("en-IN", {
    day: "2-digit",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });
}

export function LoanTimeline({ events }: { events: LoanTimelineEvent[] }) {
  if (events.length === 0) {
    return (
      <div className="rounded-[28px] border border-white/60 bg-white/75 p-6 text-[13px] text-[#5b6b8c] shadow-[0_8px_30px_rgba(15,27,51,0.06)]">
        No timeline events yet.
      </div>
    );
  }

  return (
    <div className="rounded-[28px] border border-white/60 bg-white/75 p-6 shadow-[0_8px_30px_rgba(15,27,51,0.06)] backdrop-blur-xl">
      <h2 className="mb-5 text-[16px] font-bold text-[#0f1b33]">Workflow Timeline</h2>

      <div className="flex flex-col gap-4">
        {events.map((event, index) => {
          const isFailure = event.title.toLowerCase().includes("failed");
          const Icon = isFailure ? XCircle : CATEGORY_ICONS[event.category];
          const color = isFailure ? "#EC4899" : CATEGORY_COLORS[event.category];

          return (
            <div key={`${event.timestamp}-${index}`} className="flex gap-3">
              <div className="flex flex-col items-center">
                <div
                  className="flex h-8 w-8 shrink-0 items-center justify-center rounded-xl"
                  style={{ backgroundColor: `${color}1A`, color }}
                >
                  <Icon size={16} />
                </div>
                {index < events.length - 1 && (
                  <div className="mt-1 w-px flex-1 bg-[#0f1b33]/10" />
                )}
              </div>
              <div className="min-w-0 flex-1 pb-4">
                <div className="flex items-center justify-between gap-3">
                  <span className="text-[13.5px] font-bold text-[#0f1b33]">{event.title}</span>
                  <span className="shrink-0 text-[11px] text-[#5b6b8c]">
                    {formatTimestamp(event.timestamp)}
                  </span>
                </div>
                {event.description && (
                  <p className="mt-0.5 text-[12.5px] text-[#5b6b8c]">{event.description}</p>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
