"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  BarChart3,
  FileText,
  LayoutDashboard,
  Package,
  Settings,
  Sparkles,
  Users,
  Waypoints,
  Workflow,
} from "lucide-react";
import { toast } from "sonner";
import { cn } from "@/lib/utils";

const NAV_ITEMS = [
  { label: "Overview", icon: LayoutDashboard, href: "/dashboard" },
  { label: "Applications", icon: FileText, href: null },
  { label: "Pipeline", icon: Workflow, href: null },
  { label: "Documents", icon: FileText, href: null },
  { label: "AI Agents", icon: Sparkles, href: null },
  { label: "Monitoring", icon: Waypoints, href: null },
  { label: "Reports & Audit", icon: BarChart3, href: null },
  { label: "Customers", icon: Users, href: null },
  { label: "Products", icon: Package, href: null },
  { label: "Settings", icon: Settings, href: null },
] as const;

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="flex h-full w-[248px] shrink-0 flex-col rounded-[28px] border border-white/60 bg-white/75 p-5 shadow-[0_8px_30px_rgba(15,27,51,0.06)] backdrop-blur-xl">
      <Link href="/" className="mb-8 flex items-center gap-2.5 px-1">
        <div className="flex h-9 w-9 items-center justify-center rounded-2xl bg-gradient-to-br from-[#26D9FF] via-[#3B82F6] to-[#A855F7] text-[14px] font-extrabold text-white">
          N
        </div>
        <div>
          <div
            className="text-[15px] font-extrabold leading-tight text-[#0f1b33]"
            style={{ fontFamily: "var(--font-sora)" }}
          >
            NidhiFlow AI
          </div>
          <div className="text-[10.5px] font-semibold text-[#5b6b8c]">
            Loan Operations Platform
          </div>
        </div>
      </Link>

      <nav className="flex flex-1 flex-col gap-1">
        {NAV_ITEMS.map((item) => {
          const active = item.href !== null && pathname === item.href;
          const className = cn(
            "flex items-center gap-3 rounded-2xl px-3 py-2.5 text-[13.5px] font-semibold transition-colors",
            active
              ? "bg-gradient-to-r from-[#26D9FF]/15 via-[#3B82F6]/15 to-[#A855F7]/15 text-[#1d4ed8]"
              : "text-[#5b6b8c] hover:bg-[#0f1b33]/5 hover:text-[#0f1b33]",
          );

          if (item.href) {
            return (
              <Link key={item.label} href={item.href} className={className}>
                <item.icon size={17} />
                {item.label}
              </Link>
            );
          }

          return (
            <button
              key={item.label}
              type="button"
              onClick={() => toast.info(`${item.label} is coming in a later phase`)}
              className={className}
            >
              <item.icon size={17} />
              {item.label}
            </button>
          );
        })}
      </nav>
    </aside>
  );
}
