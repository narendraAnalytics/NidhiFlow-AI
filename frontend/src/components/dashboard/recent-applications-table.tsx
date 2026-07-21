import type { RecentApplicationItem } from "@/types/dashboard";

const STATUS_CHIP_STYLES: Record<string, string> = {
  Draft: "bg-slate-100 text-slate-600",
  "Documents Uploaded": "bg-[#3B82F6]/10 text-[#1d4ed8]",
  Processing: "bg-[#F59E0B]/10 text-[#a16207]",
  "Human Review": "bg-[#A855F7]/10 text-[#7e22ce]",
  Approved: "bg-[#22C55E]/10 text-[#15803d]",
  Rejected: "bg-[#EC4899]/10 text-[#be185d]",
  Completed: "bg-[#14B8A6]/10 text-[#0f766e]",
};

function relativeTime(isoDate: string): string {
  const diffMs = Date.now() - new Date(isoDate).getTime();
  const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
  if (diffHours < 1) return "Just now";
  if (diffHours < 24) return `${diffHours}h ago`;
  const diffDays = Math.floor(diffHours / 24);
  return `${diffDays}d ago`;
}

function formatCurrency(amount: number): string {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0,
  }).format(amount);
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
            <div key={app.id} className="flex items-center gap-3 py-3">
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
                className={`shrink-0 rounded-full px-2.5 py-1 text-[11px] font-bold ${
                  STATUS_CHIP_STYLES[app.status] ?? "bg-slate-100 text-slate-600"
                }`}
              >
                {app.status}
              </span>
              <div className="w-24 shrink-0 text-right text-[13px] font-bold text-[#0f1b33]">
                {formatCurrency(app.requested_amount)}
              </div>
              <div className="w-16 shrink-0 text-right text-[11.5px] text-[#5b6b8c]">
                {relativeTime(app.created_at)}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
