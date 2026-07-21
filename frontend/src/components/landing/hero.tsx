"use client";

import Image from "next/image";
import { motion } from "framer-motion";
import { ArrowRight, Check, Play, Cloud } from "lucide-react";
import { CommandCenter } from "./command-center";

const TECH_BADGES = [
  {
    name: "Google Cloud",
    icon: "https://res.cloudinary.com/dkqbzwicr/image/upload/v1784612286/googlecloudicon_bk0ch6.png",
  },
  { name: "LangGraph", icon: "https://cdn.simpleicons.org/langgraph" },
  { name: "FastAPI", icon: "https://cdn.simpleicons.org/fastapi" },
  { name: "Docker", icon: "https://cdn.simpleicons.org/docker" },
  { name: "Kubernetes", icon: "https://cdn.simpleicons.org/kubernetes" },
  {
    name: "Firebase",
    icon: "https://res.cloudinary.com/dkqbzwicr/image/upload/v1784612286/firbaselogo_hqw3sk.png",
  },
];

export function Hero() {
  return (
    <div className="relative z-10 mx-auto flex max-w-[1240px] flex-wrap items-start gap-14 px-6 pb-6 pt-16">
      {/* Left */}
      <motion.div
        initial={{ opacity: 0, y: 24 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="flex min-w-[320px] flex-1 basis-[460px] flex-col items-start gap-6 pt-5"
      >
        <div className="inline-flex items-center gap-2 rounded-full border border-white/25 bg-white/10 px-[18px] py-2 text-[13.5px] font-bold text-[#FCD34D] backdrop-blur-xl">
          <Cloud size={17} color="#FCD34D" />
          Built on Google Cloud
        </div>

        <h1
          className="m-0 text-[clamp(38px,5.2vw,62px)] font-extrabold leading-[1.08] tracking-tight text-white"
          style={{ fontFamily: "var(--font-sora)", textWrap: "balance" }}
        >
          Intelligent Loan Operations.{" "}
          <span
            className="bg-clip-text text-transparent"
            style={{
              backgroundImage:
                "linear-gradient(92deg, #26D9FF 0%, #3B82F6 35%, #7C4DFF 65%, #EC4899 100%)",
            }}
          >
            Powered by AI Agents.
          </span>
        </h1>

        <p
          className="m-0 max-w-[520px] text-[clamp(16px,1.6vw,19px)] leading-[1.65] text-[#D7E4FF]"
          style={{ textWrap: "pretty" }}
        >
          Automate, orchestrate and optimize the entire loan lifecycle with
          five specialized AI agents working 24/7 — from document intake to
          compliance, monitoring and audit.
        </p>

        <div className="flex flex-wrap gap-4">
          <a
            href="#trial"
            className="nf-cta inline-flex items-center gap-2.5 rounded-[20px] bg-gradient-to-r from-[#26D9FF] via-[#3B82F6] to-[#A855F7] px-[30px] py-4 text-[16px] font-extrabold text-white shadow-[0_10px_30px_rgba(59,130,246,0.4),0_0_40px_rgba(38,217,255,0.25)] transition-all"
          >
            Start Free Trial
            <ArrowRight size={18} />
          </a>
          <a
            href="#tour"
            className="nf-tour inline-flex items-center gap-2.5 rounded-[20px] border border-white/25 bg-white/10 px-7 py-4 text-[16px] font-bold text-white backdrop-blur-xl transition-all"
          >
            <span className="flex h-[30px] w-[30px] items-center justify-center rounded-full bg-gradient-to-br from-[#26D9FF] to-[#7C4DFF] shadow-[0_3px_12px_rgba(124,77,255,0.4)]">
              <Play size={12} fill="#fff" color="#fff" />
            </span>
            Watch Platform Tour
          </a>
        </div>

        <div className="flex flex-wrap gap-x-5 gap-y-2.5 text-[13.5px] font-semibold text-[#86EFAC]">
          <span className="inline-flex items-center gap-1.5">
            <Check size={15} strokeWidth={2.6} /> No credit card
          </span>
          <span className="inline-flex items-center gap-1.5">
            <Check size={15} strokeWidth={2.6} /> Human-in-the-loop decisions
          </span>
          <span className="inline-flex items-center gap-1.5">
            <Check size={15} strokeWidth={2.6} /> Cancel anytime
          </span>
        </div>

        <div className="mt-1.5 flex flex-col gap-3">
          <span className="text-[11.5px] font-extrabold uppercase tracking-[0.14em] text-[#F9A8D4]">
            Powered by trusted technology
          </span>
          <div className="flex flex-wrap gap-2.5">
            {TECH_BADGES.map((tb) => (
              <span
                key={tb.name}
                className="nf-badge inline-flex items-center gap-2.5 rounded-full border border-white/20 bg-white/10 px-4 py-2.5 text-[13px] font-bold text-white backdrop-blur-xl transition-transform"
              >
                <span className="flex h-5 w-5 items-center justify-center rounded-full bg-white/90">
                  {tb.icon.includes("simpleicons.org") ? (
                    // eslint-disable-next-line @next/next/no-img-element -- next/image blocks remote SVG optimization; simple-icons serves fixed-size SVGs that don't need it
                    <img src={tb.icon} alt="" width={13} height={13} className="object-contain" />
                  ) : (
                    <Image src={tb.icon} alt="" width={13} height={13} unoptimized className="object-contain" />
                  )}
                </span>
                {tb.name}
              </span>
            ))}
          </div>
        </div>
      </motion.div>

      {/* Right: AI Command Center */}
      <div className="flex min-w-[320px] flex-1 basis-[520px] flex-col items-center">
        <CommandCenter />
      </div>
    </div>
  );
}
