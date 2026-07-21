"use client";

import Link from "next/link";
import type { User } from "firebase/auth";
import { Bell, Plus, Search } from "lucide-react";
import { toast } from "sonner";

export function Topbar({ user }: { user: User }) {
  const displayName = user.displayName ?? user.email?.split("@")[0] ?? "there";

  return (
    <header className="flex flex-wrap items-center justify-between gap-4 rounded-[28px] border border-white/60 bg-white/75 px-6 py-4 shadow-[0_8px_30px_rgba(15,27,51,0.06)] backdrop-blur-xl">
      <div>
        <h1
          className="text-[22px] font-extrabold text-[#0f1b33]"
          style={{ fontFamily: "var(--font-sora)" }}
        >
          Dashboard 👋
        </h1>
        <p className="text-[13px] text-[#5b6b8c]">
          Welcome back, {displayName}! Here&apos;s what&apos;s happening with your loan
          operations today.
        </p>
      </div>

      <div className="flex items-center gap-3">
        <div className="hidden items-center gap-2 rounded-2xl border border-[#0f1b33]/10 bg-white/60 px-3.5 py-2.5 md:flex">
          <Search size={16} className="text-[#5b6b8c]" />
          <input
            type="text"
            placeholder="Search loans, applications, borrowers..."
            className="w-56 bg-transparent text-[13px] text-[#0f1b33] placeholder:text-[#5b6b8c]/60 outline-none"
            onFocus={() => toast.info("Search is coming in a later phase")}
            readOnly
          />
        </div>

        <button
          type="button"
          onClick={() => toast.info("Notifications are coming in a later phase")}
          className="flex h-10 w-10 items-center justify-center rounded-2xl border border-[#0f1b33]/10 bg-white/60 text-[#5b6b8c] hover:text-[#0f1b33]"
        >
          <Bell size={17} />
        </button>

        <Link
          href="/loan-application"
          className="nf-cta inline-flex items-center gap-2 rounded-2xl bg-gradient-to-r from-[#26D9FF] via-[#3B82F6] to-[#A855F7] px-4 py-2.5 text-[13.5px] font-extrabold text-white shadow-[0_10px_30px_rgba(59,130,246,0.35)] transition-all"
        >
          <Plus size={16} />
          New Application
        </Link>
      </div>
    </header>
  );
}
