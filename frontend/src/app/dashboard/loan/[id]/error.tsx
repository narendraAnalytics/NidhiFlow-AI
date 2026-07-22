"use client";

import { useEffect } from "react";

export default function LoanDetailError({
  error,
  unstable_retry,
}: {
  error: Error & { digest?: string };
  unstable_retry: () => void;
}) {
  useEffect(() => {
    console.error(error);
  }, [error]);

  return (
    <div className="rounded-[28px] border border-white/60 bg-white/75 p-8 text-center shadow-[0_8px_30px_rgba(15,27,51,0.06)] backdrop-blur-xl">
      <h2 className="text-[16px] font-bold text-[#0f1b33]">Couldn&apos;t load this loan</h2>
      <p className="mt-1 text-[13px] text-[#5b6b8c]">Something went wrong fetching this page.</p>
      <button
        onClick={() => unstable_retry()}
        className="mt-4 rounded-full bg-[#1d4ed8] px-4 py-2 text-[13px] font-semibold text-white"
      >
        Try again
      </button>
    </div>
  );
}
