"use client";

import {
  Area,
  AreaChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { TrendPoint } from "@/types/dashboard";

export function ApplicationTrendChart({ trend }: { trend: TrendPoint[] }) {
  const data = trend.map((point) => ({
    ...point,
    label: new Date(point.date).toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
    }),
  }));

  return (
    <div className="rounded-[28px] border border-white/60 bg-white/75 p-6 shadow-[0_8px_30px_rgba(15,27,51,0.06)] backdrop-blur-xl">
      <h2 className="mb-4 text-[16px] font-bold text-[#0f1b33]">Application Trend</h2>
      <ResponsiveContainer width="100%" height={240}>
        <AreaChart data={data} margin={{ left: -20 }}>
          <defs>
            <linearGradient id="applicationsGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#3B82F6" stopOpacity={0.35} />
              <stop offset="100%" stopColor="#3B82F6" stopOpacity={0} />
            </linearGradient>
            <linearGradient id="approvedGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#22C55E" stopOpacity={0.35} />
              <stop offset="100%" stopColor="#22C55E" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(15,27,51,0.08)" />
          <XAxis dataKey="label" tick={{ fontSize: 11, fill: "#5b6b8c" }} minTickGap={24} />
          <YAxis tick={{ fontSize: 11, fill: "#5b6b8c" }} allowDecimals={false} />
          <Tooltip
            contentStyle={{
              borderRadius: 16,
              border: "1px solid rgba(15,27,51,0.1)",
              fontSize: 12.5,
            }}
          />
          <Legend wrapperStyle={{ fontSize: 12.5 }} />
          <Area
            type="monotone"
            dataKey="applications"
            name="Applications"
            stroke="#3B82F6"
            strokeWidth={2.5}
            fill="url(#applicationsGradient)"
          />
          <Area
            type="monotone"
            dataKey="approved"
            name="Approved"
            stroke="#22C55E"
            strokeWidth={2.5}
            fill="url(#approvedGradient)"
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
