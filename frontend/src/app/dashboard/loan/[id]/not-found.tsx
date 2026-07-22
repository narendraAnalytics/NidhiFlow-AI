import Link from "next/link";

export default function LoanNotFound() {
  return (
    <div className="rounded-[28px] border border-white/60 bg-white/75 p-8 text-center shadow-[0_8px_30px_rgba(15,27,51,0.06)] backdrop-blur-xl">
      <h2 className="text-[16px] font-bold text-[#0f1b33]">Loan not found</h2>
      <p className="mt-1 text-[13px] text-[#5b6b8c]">
        This loan application doesn&apos;t exist or has been removed.
      </p>
      <Link
        href="/dashboard"
        className="mt-4 inline-block text-[13px] font-semibold text-[#1d4ed8]"
      >
        Back to dashboard
      </Link>
    </div>
  );
}
