import type { ReactNode } from "react";
import type { User } from "firebase/auth";
import { Sidebar } from "./sidebar";
import { Topbar } from "./topbar";

export function DashboardShell({
  user,
  children,
}: {
  user: User;
  children: ReactNode;
}) {
  return (
    <div className="relative min-h-screen overflow-hidden bg-[#f8fbff] px-4 py-5 sm:px-6 lg:px-8">
      <div className="pointer-events-none absolute -left-32 -top-32 h-[420px] w-[420px] rounded-full bg-[#EAFBFF] blur-3xl" />
      <div className="pointer-events-none absolute right-[-10%] top-40 h-[380px] w-[380px] rounded-full bg-[#F5F1FF] blur-3xl" />
      <div className="pointer-events-none absolute bottom-[-15%] left-1/3 h-[420px] w-[420px] rounded-full bg-[#FFF8FC] blur-3xl" />

      <div className="relative mx-auto flex max-w-[1600px] gap-6">
        <Sidebar />
        <div className="flex min-w-0 flex-1 flex-col gap-6">
          <Topbar user={user} />
          <main className="flex flex-col gap-6 pb-8">{children}</main>
        </div>
      </div>
    </div>
  );
}
