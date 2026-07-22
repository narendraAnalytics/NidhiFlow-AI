import Link from "next/link";
import type { RecentApplicationItem } from "@/types/dashboard";
import { getStatusChipStyle } from "@/lib/status-styles";
import { formatCurrency } from "@/lib/format";

function relativeTime(isoDate: string): string {
  const diffMs = Date.now() - new Date(isoDate).getTime();
  const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
  if (diffHours < 1) return "Just now";
  if (diffHours < 24) return `${diffHours}h ago`;
  const diffDays = Math.floor(diffHours / 24);
  return `${diffDays}d ago`;
}

export function RecentApplicationsTable({
  applications,
}: {
  applications: RecentApplicationItem[];
}) {
  return (
    <div className="rounded-[28px] border border-white/60 bg-white/75 p-6 shadow-[0_8px_30px_rgba(15,27,51,0.06)] backdrop-blur-xl">
      <h2 className="mb-4 text-[16px] font-bold text-[#0f1b33]">Recent Applications</h2>

      {applications.length === 0 ? (
        <p className="text-[13px] text-[#5b6b8c]">No applications yet.</p>
      ) : (
        <div className="flex flex-col divide-y divide-[#0f1b33]/8">
          {applications.map((app) => (
            <Link
              key={app.id}
              href={`/dashboard/loan/${app.id}`}
              className="flex items-center gap-3 py-3 transition-colors hover:bg-[#0f1b33]/[0.03]"
            >
              <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-[#26D9FF] to-[#A855F7] text-[12px] font-bold text-white">
                {app.customer_name.charAt(0).toUpperCase()}
              </div>
              <div className="min-w-0 flex-1">
                <div className="truncate text-[13.5px] font-bold text-[#0f1b33]">
                  {app.loan_type} Loan
                </div>
                <div className="truncate text-[11.5px] text-[#5b6b8c]">{app.customer_name}</div>
              </div>
              <span
                className={`shrink-0 rounded-full px-2.5 py-1 text-[11px] font-bold ${getStatusChipStyle(app.status)}`}
              >
                {app.status}
              </span>
              <div className="w-24 shrink-0 text-right text-[13px] font-bold text-[#0f1b33]">
                {formatCurrency(app.requested_amount)}
              </div>
              <div className="w-16 shrink-0 text-right text-[11.5px] text-[#5b6b8c]">
                {relativeTime(app.created_at)}
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
