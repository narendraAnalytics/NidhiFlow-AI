"use client";

import { useState } from "react";
import Image from "next/image";
import { Menu, X, ArrowRight } from "lucide-react";
import { cn } from "@/lib/utils";

const LOGO_URL =
  "https://res.cloudinary.com/dkqbzwicr/image/upload/v1784610412/LogoNidhiFlowAI_wqxhyg.png";

const NAV_LINKS = [
  { href: "#platform", label: "Platform" },
  { href: "#solutions", label: "Solutions" },
  { href: "#pricing", label: "Pricing" },
  { href: "#enterprise", label: "Enterprise" },
];

export function Navbar() {
  const [menuOpen, setMenuOpen] = useState(false);

  return (
    <div className="sticky top-3.5 z-50 px-4">
      <nav className="mx-auto flex max-w-[1240px] items-center gap-4 rounded-[28px] border border-white/15 bg-white/10 px-3 py-2.5 pl-4 shadow-[0_12px_40px_rgba(0,0,0,0.25)] backdrop-blur-2xl">
        <div className="flex flex-shrink-0 items-center gap-2.5">
          <Image
            src={LOGO_URL}
            alt="NidhiFlow AI"
            width={38}
            height={38}
            priority
            unoptimized
            className="object-contain drop-shadow-[0_2px_8px_rgba(124,77,255,0.45)]"
          />
          <span
            className="text-[18px] font-extrabold tracking-tight text-white"
            style={{ fontFamily: "var(--font-sora)" }}
          >
            NidhiFlow{" "}
            <span className="bg-gradient-to-r from-[#26D9FF] to-[#7C4DFF] bg-clip-text text-transparent">
              AI
            </span>
          </span>
        </div>

        {/* Desktop */}
        <div className="ml-auto hidden flex-wrap items-center gap-1 md:flex">
          {NAV_LINKS.map((link) => (
            <a
              key={link.href}
              href={link.href}
              className="nf-navlink rounded-2xl px-3.5 py-2 text-[14.5px] font-semibold text-white/90"
            >
              {link.label}
            </a>
          ))}
        </div>
        <div className="hidden flex-shrink-0 items-center gap-2.5 md:flex">
          <a
            href="#demo"
            className="nf-cta inline-flex items-center gap-2 rounded-[18px] bg-gradient-to-r from-[#26D9FF] via-[#3B82F6] to-[#A855F7] px-5 py-2.5 text-[14.5px] font-bold text-white shadow-[0_6px_20px_rgba(124,77,255,0.4)] transition-all"
          >
            Request Demo <ArrowRight size={15} />
          </a>
        </div>

        {/* Mobile toggle */}
        <button
          onClick={() => setMenuOpen((v) => !v)}
          aria-label="Menu"
          className="ml-auto flex h-[42px] w-[42px] items-center justify-center rounded-2xl border border-white/20 bg-white/10 md:hidden"
        >
          {menuOpen ? <X size={20} color="#fff" /> : <Menu size={20} color="#fff" />}
        </button>
      </nav>

      <div
        className={cn(
          "mx-auto mt-2 flex max-w-[1240px] origin-top flex-col gap-1 overflow-hidden rounded-3xl border border-white/15 bg-[#0f1b33]/90 p-3.5 shadow-[0_16px_48px_rgba(0,0,0,0.35)] backdrop-blur-2xl transition-all duration-200 md:hidden",
          menuOpen ? "max-h-[420px] opacity-100" : "pointer-events-none max-h-0 p-0 opacity-0",
        )}
      >
        {NAV_LINKS.map((link) => (
          <a
            key={link.href}
            href={link.href}
            className="nf-navlink rounded-[14px] px-4 py-3 font-semibold text-white/90"
          >
            {link.label}
          </a>
        ))}
        <a
          href="#demo"
          className="mt-1 rounded-2xl bg-gradient-to-r from-[#26D9FF] via-[#3B82F6] to-[#A855F7] px-4 py-3.5 text-center font-bold text-white shadow-[0_6px_20px_rgba(124,77,255,0.4)]"
        >
          Request Demo →
        </a>
      </div>
    </div>
  );
}
