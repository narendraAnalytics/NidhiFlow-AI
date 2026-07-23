"use client";

import { useState } from "react";
import { Download, Loader2 } from "lucide-react";
import { toast } from "sonner";
import { useAuth } from "@/contexts/auth-context";
import { downloadLoanReport } from "@/lib/api";

export function DownloadReportButton({ loanId }: { loanId: string }) {
  const { user } = useAuth();
  const [downloading, setDownloading] = useState(false);

  const onDownload = async () => {
    if (!user) return;
    setDownloading(true);
    try {
      const idToken = await user.getIdToken();
      const blob = await downloadLoanReport(loanId, idToken);
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `loan-report-${loanId}.pdf`;
      document.body.appendChild(link);
      link.click();
      link.remove();
      URL.revokeObjectURL(url);
    } catch {
      toast.error("Could not download the report. Please try again.");
    } finally {
      setDownloading(false);
    }
  };

  return (
    <button
      type="button"
      onClick={onDownload}
      disabled={downloading}
      className="inline-flex shrink-0 items-center justify-center gap-1.5 rounded-full border border-[#e2e8f5] bg-white px-3.5 py-1.5 text-[12px] font-bold text-[#0f1b33] transition-colors hover:bg-[#f8fbff] disabled:cursor-not-allowed disabled:opacity-60"
    >
      {downloading ? <Loader2 size={14} className="animate-spin" /> : <Download size={14} />}
      PDF Report
    </button>
  );
}
