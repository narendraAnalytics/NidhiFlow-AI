import type { LucideIcon } from "lucide-react";
import { ArrowUp } from "lucide-react";
import { Sparkline } from "./sparkline";

export function KpiCard({
  icon: Icon,
  label,
  value,
  deltaLabel,
  color,
  sparklineData,
}: {
  icon: LucideIcon;
  label: string;
  value: string;
  deltaLabel?: string;
  color: string;
  sparklineData: number[];
}) {
  return (
    <div className="rounded-[24px] border border-white/60 bg-white/75 p-5 shadow-[0_8px_30px_rgba(15,27,51,0.06)] backdrop-blur-xl transition-transform hover:-translate-y-1">
      <div className="mb-3 flex items-center gap-3">
        <div
          className="flex h-10 w-10 items-center justify-center rounded-2xl"
          style={{ backgroundColor: `${color}1A`, color }}
        >
          <Icon size={19} />
        </div>
        <span className="text-[13px] font-semibold text-[#5b6b8c]">{label}</span>
      </div>
      <div className="mb-1 text-[26px] font-extrabold text-[#0f1b33]">{value}</div>
      {deltaLabel && (
        <div className="mb-2 flex items-center gap-1 text-[12.5px] font-bold text-[#15803d]">
          <ArrowUp size={13} />
          {deltaLabel}
        </div>
      )}
      <Sparkline data={sparklineData} color={color} />
    </div>
  );
}
