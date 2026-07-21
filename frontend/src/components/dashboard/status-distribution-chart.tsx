"use client";

import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";
import type { StatusDistributionSlice } from "@/types/dashboard";

const STATUS_COLORS: Record<string, string> = {
  Draft: "#94a3b8",
  "In Process": "#3B82F6",
  Approved: "#22C55E",
  Disbursed: "#14B8A6",
  Rejected: "#EC4899",
};

export function StatusDistributionChart({
  distribution,
}: {
  distribution: StatusDistributionSlice[];
}) {
  const total = distribution.reduce((sum, slice) => sum + slice.count, 0);

  return (
    <div className="rounded-[28px] border border-white/60 bg-white/75 p-6 shadow-[0_8px_30px_rgba(15,27,51,0.06)] backdrop-blur-xl">
      <h2 className="mb-4 text-[16px] font-bold text-[#0f1b33]">
        Application Status Distribution
      </h2>
      <div className="flex items-center gap-4">
        <div className="relative h-[180px] w-[180px] shrink-0">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={distribution}
                dataKey="count"
                nameKey="status"
                innerRadius={55}
                outerRadius={80}
                paddingAngle={2}
                isAnimationActive={false}
              >
                {distribution.map((slice) => (
                  <Cell
                    key={slice.status}
                    fill={STATUS_COLORS[slice.status] ?? "#94a3b8"}
                  />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{
                  borderRadius: 16,
                  border: "1px solid rgba(15,27,51,0.1)",
                  fontSize: 12.5,
                }}
              />
            </PieChart>
          </ResponsiveContainer>
          <div className="pointer-events-none absolute inset-0 flex flex-col items-center justify-center">
            <span className="text-[20px] font-extrabold text-[#0f1b33]">{total}</span>
            <span className="text-[11px] font-semibold text-[#5b6b8c]">Total</span>
          </div>
        </div>
        <div className="flex flex-1 flex-col gap-2.5">
          {distribution.map((slice) => (
            <div key={slice.status} className="flex items-center justify-between text-[13px]">
              <div className="flex items-center gap-2">
                <span
                  className="h-2.5 w-2.5 rounded-full"
                  style={{ backgroundColor: STATUS_COLORS[slice.status] ?? "#94a3b8" }}
                />
                <span className="font-semibold text-[#5b6b8c]">{slice.status}</span>
              </div>
              <span className="font-bold text-[#0f1b33]">
                {slice.percentage}% ({slice.count})
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
