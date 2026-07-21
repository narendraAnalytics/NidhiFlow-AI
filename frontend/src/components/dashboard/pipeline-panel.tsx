import { CheckCircle2, ClipboardList, FileCheck2, Landmark, ShieldCheck } from "lucide-react";
import type { PipelineStageCount } from "@/types/dashboard";

const STAGE_ICONS = [ClipboardList, ShieldCheck, Landmark, CheckCircle2, FileCheck2];
const STAGE_COLORS = ["#3B82F6", "#F59E0B", "#A855F7", "#22C55E", "#14B8A6"];

export function PipelinePanel({
  pipeline,
  conversionRate,
}: {
  pipeline: PipelineStageCount[];
  conversionRate: number;
}) {
  return (
    <div className="rounded-[28px] border border-white/60 bg-white/75 p-6 shadow-[0_8px_30px_rgba(15,27,51,0.06)] backdrop-blur-xl">
      <h2 className="mb-5 text-[16px] font-bold text-[#0f1b33]">Loan Application Pipeline</h2>

      <div className="grid grid-cols-2 gap-4 sm:grid-cols-5">
        {pipeline.map((stage, index) => {
          const Icon = STAGE_ICONS[index % STAGE_ICONS.length];
          const color = STAGE_COLORS[index % STAGE_COLORS.length];
          return (
            <div key={stage.stage} className="flex flex-col items-center text-center">
              <div
                className="mb-2 flex h-11 w-11 items-center justify-center rounded-2xl"
                style={{ backgroundColor: `${color}1A`, color }}
              >
                <Icon size={20} />
              </div>
              <span className="text-[12.5px] font-semibold text-[#5b6b8c]">{stage.stage}</span>
              <span className="text-[19px] font-extrabold text-[#0f1b33]">{stage.count}</span>
            </div>
          );
        })}
      </div>

      <div className="mt-6 border-t border-[#0f1b33]/10 pt-5">
        <div className="mb-2 flex items-center justify-between">
          <span className="text-[13px] font-semibold text-[#5b6b8c]">Conversion Rate</span>
          <span className="text-[13px] font-bold text-[#15803d]">
            {(conversionRate * 100).toFixed(1)}%
          </span>
        </div>
        <div className="h-2.5 w-full overflow-hidden rounded-full bg-[#0f1b33]/8">
          <div
            className="h-full rounded-full bg-gradient-to-r from-[#26D9FF] via-[#3B82F6] to-[#A855F7]"
            style={{ width: `${Math.min(conversionRate * 100, 100)}%` }}
          />
        </div>
      </div>
    </div>
  );
}
