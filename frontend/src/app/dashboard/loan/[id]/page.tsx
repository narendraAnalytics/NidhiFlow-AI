import { notFound } from "next/navigation";
import { getLoanTimeline } from "@/lib/api";
import { LoanSummaryCard } from "@/components/loan/loan-summary-card";
import { LoanTimeline } from "@/components/loan/loan-timeline";
import { AgentPipeline } from "@/components/loan/agent-pipeline";
import { DownloadReportButton } from "@/components/loan/download-report-button";

export default async function LoanDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const timeline = await getLoanTimeline(id);

  if (!timeline) {
    notFound();
  }

  const { loan, customer, validation_summary: validationSummary, events } = timeline;

  return (
    <div className="flex flex-col gap-6">
      <LoanSummaryCard
        loan={loan}
        customer={customer}
        validationSummary={validationSummary}
        actions={<DownloadReportButton loanId={id} />}
      />
      <AgentPipeline events={events} />
      <LoanTimeline events={events} />
    </div>
  );
}
