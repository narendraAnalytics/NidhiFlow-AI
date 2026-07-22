import { notFound } from "next/navigation";
import { getLoanTimeline } from "@/lib/api";
import { getStatusChipStyle } from "@/lib/status-styles";
import { formatCurrency } from "@/lib/format";
import { LoanTimeline } from "@/components/loan/loan-timeline";

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
      <div className="rounded-[28px] border border-white/60 bg-white/75 p-6 shadow-[0_8px_30px_rgba(15,27,51,0.06)] backdrop-blur-xl">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <h1 className="text-[19px] font-extrabold text-[#0f1b33]">
              {loan.loan_type} Loan — {customer.full_name}
            </h1>
            <p className="mt-1 text-[13px] text-[#5b6b8c]">
              {formatCurrency(loan.requested_amount)} · Applied{" "}
              {new Date(loan.created_at).toLocaleDateString("en-IN", {
                day: "2-digit",
                month: "short",
                year: "numeric",
              })}
            </p>
          </div>
          <span
            className={`shrink-0 rounded-full px-3 py-1.5 text-[12px] font-bold ${getStatusChipStyle(loan.status)}`}
          >
            {loan.status}
          </span>
        </div>

        {validationSummary && (
          <div className="mt-5 border-t border-[#0f1b33]/10 pt-5">
            <div className="mb-3 flex items-center justify-between">
              <span className="text-[13px] font-semibold text-[#5b6b8c]">
                Validation — {validationSummary.validation_status}
              </span>
              <span className="text-[13px] font-bold text-[#0f1b33]">
                {(validationSummary.confidence * 100).toFixed(0)}% confidence
              </span>
            </div>
            {validationSummary.missing_documents.length > 0 && (
              <p className="text-[12.5px] text-[#be185d]">
                Missing documents: {validationSummary.missing_documents.join(", ")}
              </p>
            )}
            {validationSummary.field_mismatches.length > 0 && (
              <ul className="mt-1 list-disc pl-4 text-[12.5px] text-[#be185d]">
                {validationSummary.field_mismatches.map((mismatch) => (
                  <li key={mismatch}>{mismatch}</li>
                ))}
              </ul>
            )}
          </div>
        )}
      </div>

      <LoanTimeline events={events} />
    </div>
  );
}
