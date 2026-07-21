"use client";

import { useEffect, useState } from "react";
import { CheckCircle2, Clock3, FileStack, Target, Timer } from "lucide-react";
import { useAuth } from "@/contexts/auth-context";
import { getDashboardStats } from "@/lib/api";
import type { DashboardStatsResponse } from "@/types/dashboard";
import { KpiCard } from "@/components/dashboard/kpi-card";
import { PipelinePanel } from "@/components/dashboard/pipeline-panel";
import { AiAgentPanel } from "@/components/dashboard/ai-agent-panel";
import { ApplicationTrendChart } from "@/components/dashboard/application-trend-chart";
import { StatusDistributionChart } from "@/components/dashboard/status-distribution-chart";
import { RecentApplicationsTable } from "@/components/dashboard/recent-applications-table";
import { SummaryBar } from "@/components/dashboard/summary-bar";

function periodDelta(series: number[]): string | undefined {
  if (series.length < 14) return undefined;
  const lastWeek = series.slice(-7).reduce((a, b) => a + b, 0);
  const priorWeek = series.slice(-14, -7).reduce((a, b) => a + b, 0);
  if (priorWeek === 0) return undefined;
  const change = ((lastWeek - priorWeek) / priorWeek) * 100;
  return `${change >= 0 ? "+" : ""}${change.toFixed(1)}% vs last 7 days`;
}

export default function DashboardOverviewPage() {
  const { user } = useAuth();
  const [stats, setStats] = useState<DashboardStatsResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!user) return;
    let cancelled = false;

    (async () => {
      try {
        const idToken = await user.getIdToken();
        const data = await getDashboardStats(idToken);
        if (!cancelled) setStats(data);
      } catch {
        if (!cancelled) setError("Failed to load dashboard data.");
      }
    })();

    return () => {
      cancelled = true;
    };
  }, [user]);

  if (error) {
    return (
      <div className="rounded-[28px] border border-white/60 bg-white/75 p-6 text-[13.5px] text-[#be185d] shadow-[0_8px_30px_rgba(15,27,51,0.06)]">
        {error}
      </div>
    );
  }

  if (!stats) {
    return (
      <div className="rounded-[28px] border border-white/60 bg-white/75 p-6 text-[13.5px] text-[#5b6b8c] shadow-[0_8px_30px_rgba(15,27,51,0.06)]">
        Loading dashboard…
      </div>
    );
  }

  const applicationsSeries = stats.trend.map((p) => p.applications);
  const approvedSeries = stats.trend.map((p) => p.approved);

  return (
    <>
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-5">
        <KpiCard
          icon={FileStack}
          label="Total Applications"
          value={stats.total_applications.toLocaleString()}
          deltaLabel={periodDelta(applicationsSeries)}
          color="#3B82F6"
          sparklineData={applicationsSeries}
        />
        <KpiCard
          icon={Clock3}
          label="Applications in Process"
          value={stats.in_process.toLocaleString()}
          color="#F59E0B"
          sparklineData={applicationsSeries}
        />
        <KpiCard
          icon={CheckCircle2}
          label="Applications Approved"
          value={stats.approved.toLocaleString()}
          deltaLabel={periodDelta(approvedSeries)}
          color="#22C55E"
          sparklineData={approvedSeries}
        />
        <KpiCard
          icon={Timer}
          label="Avg. Processing Time"
          value={
            stats.avg_processing_days === null ? "—" : `${stats.avg_processing_days.toFixed(1)}d`
          }
          color="#A855F7"
          sparklineData={applicationsSeries}
        />
        <KpiCard
          icon={Target}
          label="Success Rate"
          value={`${(stats.success_rate * 100).toFixed(1)}%`}
          color="#EC4899"
          sparklineData={approvedSeries}
        />
      </div>

      <div className="grid grid-cols-1 gap-6 xl:grid-cols-[1.4fr_1fr]">
        <PipelinePanel pipeline={stats.pipeline} conversionRate={stats.conversion_rate} />
        <AiAgentPanel />
      </div>

      <div className="grid grid-cols-1 gap-6 xl:grid-cols-2">
        <ApplicationTrendChart trend={stats.trend} />
        <StatusDistributionChart distribution={stats.status_distribution} />
      </div>

      <RecentApplicationsTable applications={stats.recent} />

      <SummaryBar totalDisbursedAmount={stats.total_disbursed_amount} />
    </>
  );
}
