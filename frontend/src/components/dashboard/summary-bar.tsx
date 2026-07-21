import { Activity, ShieldCheck, Sparkles, Timer, Users } from "lucide-react";
import { PreviewBadge } from "./preview-badge";

function formatCurrency(amount: number): string {
  if (amount >= 10000000) return `₹${(amount / 10000000).toFixed(2)} Cr`;
  if (amount >= 100000) return `₹${(amount / 100000).toFixed(2)} L`;
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0,
  }).format(amount);
}

export function SummaryBar({ totalDisbursedAmount }: { totalDisbursedAmount: number }) {
  const cards = [
    {
      icon: Users,
      color: "#3B82F6",
      label: "Active Users",
      value: "—",
      preview: true,
    },
    {
      icon: Timer,
      color: "#22C55E",
      label: "System Uptime",
      value: "—",
      preview: true,
    },
    {
      icon: ShieldCheck,
      color: "#14B8A6",
      label: "Total Loans Disbursed",
      value: formatCurrency(totalDisbursedAmount),
      preview: false,
    },
    {
      icon: Sparkles,
      color: "#F59E0B",
      label: "Data Quality Score",
      value: "—",
      preview: true,
    },
    {
      icon: Activity,
      color: "#A855F7",
      label: "Compliance Score",
      value: "—",
      preview: true,
    },
  ];

  return (
    <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-5">
      {cards.map((card) => (
        <div
          key={card.label}
          className="flex items-center gap-3 rounded-[20px] border border-white/60 bg-white/75 p-4 shadow-[0_8px_30px_rgba(15,27,51,0.06)] backdrop-blur-xl"
        >
          <div
            className="flex h-9 w-9 shrink-0 items-center justify-center rounded-2xl"
            style={{ backgroundColor: `${card.color}1A`, color: card.color }}
          >
            <card.icon size={17} />
          </div>
          <div className="min-w-0">
            <div className="flex items-center gap-1.5">
              <span className="truncate text-[11.5px] font-semibold text-[#5b6b8c]">
                {card.label}
              </span>
              {card.preview && <PreviewBadge />}
            </div>
            <span className="text-[15px] font-extrabold text-[#0f1b33]">{card.value}</span>
          </div>
        </div>
      ))}
    </div>
  );
}
