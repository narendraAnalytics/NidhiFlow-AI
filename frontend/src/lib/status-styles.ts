export const STATUS_CHIP_STYLES: Record<string, string> = {
  Draft: "bg-slate-100 text-slate-600",
  "Documents Uploaded": "bg-[#3B82F6]/10 text-[#1d4ed8]",
  Processing: "bg-[#F59E0B]/10 text-[#a16207]",
  "Human Review": "bg-[#A855F7]/10 text-[#7e22ce]",
  Approved: "bg-[#22C55E]/10 text-[#15803d]",
  Rejected: "bg-[#EC4899]/10 text-[#be185d]",
  Completed: "bg-[#14B8A6]/10 text-[#0f766e]",
};

export function getStatusChipStyle(status: string): string {
  return STATUS_CHIP_STYLES[status] ?? "bg-slate-100 text-slate-600";
}
