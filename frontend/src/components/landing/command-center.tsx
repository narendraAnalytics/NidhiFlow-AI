"use client";

import { useEffect, useRef, useState } from "react";
import Image from "next/image";
import { motion } from "framer-motion";
import { Database, HardDrive } from "lucide-react";

const LOGO_URL =
  "https://res.cloudinary.com/dkqbzwicr/image/upload/v1784610412/LogoNidhiFlowAI_wqxhyg.png";

const AGENTS = [
  {
    n: "1",
    title: "Document Intelligence",
    desc: "Extracts and classifies documents with AI-powered OCR.",
    x: 212,
    y: 12,
    iconBg: "linear-gradient(135deg,#22C55E,#16A34A)",
    shadow: "rgba(34,197,94,.28)",
    float: "nfFloat 5s ease-in-out infinite",
  },
  {
    n: "2",
    title: "Validation & Compliance",
    desc: "Validates borrower data and checks regulatory compliance.",
    x: 4,
    y: 170,
    iconBg: "linear-gradient(135deg,#F59E0B,#F97316)",
    shadow: "rgba(245,158,11,.28)",
    float: "nfFloat2 6s ease-in-out .6s infinite",
  },
  {
    n: "3",
    title: "Pipeline Orchestrator",
    desc: "Orchestrates data pipelines seamlessly across systems.",
    x: 420,
    y: 170,
    iconBg: "linear-gradient(135deg,#A855F7,#7C4DFF)",
    shadow: "rgba(168,85,247,.3)",
    float: "nfFloat 5.5s ease-in-out 1.1s infinite",
  },
  {
    n: "4",
    title: "Monitoring & Self-Healing",
    desc: "Monitors in real time and auto-recovers from failures.",
    x: 4,
    y: 620,
    iconBg: "linear-gradient(135deg,#EC4899,#DB2777)",
    shadow: "rgba(236,72,153,.28)",
    float: "nfFloat2 6.5s ease-in-out .3s infinite",
  },
  {
    n: "5",
    title: "Reporting & Audit",
    desc: "Generates insights and audit-ready reports instantly.",
    x: 420,
    y: 620,
    iconBg: "linear-gradient(135deg,#5CA9FF,#3B82F6)",
    shadow: "rgba(92,169,255,.3)",
    float: "nfFloat 5.2s ease-in-out .9s infinite",
  },
];

const INFRA = [
  {
    name: "Cloud SQL",
    iconBg: "linear-gradient(135deg,#5CA9FF,#3B82F6)",
    glow: "rgba(92,169,255,.35)",
    Icon: Database,
  },
  {
    name: "Firebase",
    iconBg: "linear-gradient(135deg,#F59E0B,#F97316)",
    glow: "rgba(245,158,11,.35)",
    logo: "https://res.cloudinary.com/dkqbzwicr/image/upload/v1784612286/firbaselogo_hqw3sk.png",
  },
  {
    name: "Cloud Storage",
    iconBg: "linear-gradient(135deg,#26D9FF,#0EA5E9)",
    glow: "rgba(38,217,255,.35)",
    Icon: HardDrive,
  },
];

export function CommandCenter() {
  const wrapRef = useRef<HTMLDivElement>(null);
  const [scale, setScale] = useState(1);

  useEffect(() => {
    const el = wrapRef.current;
    if (!el) return;
    const ro = new ResizeObserver((entries) => {
      const w = entries[0].contentRect.width;
      if (w > 0) setScale(Math.min(1, w / 640));
    });
    ro.observe(el);
    return () => ro.disconnect();
  }, []);

  const outerH = Math.round(1000 * scale);

  return (
    <div ref={wrapRef} className="relative w-full max-w-[640px]" style={{ height: outerH }}>
      <div
        className="absolute left-1/2 top-0 h-[1000px] w-[640px] origin-top"
        style={{ transform: `translateX(-50%) scale(${scale})` }}
      >
        {/* connector lines */}
        <svg width="640" height="1000" viewBox="0 0 640 1000" className="pointer-events-none absolute inset-0">
          <defs>
            <linearGradient id="nfl1" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0" stopColor="#22C55E" />
              <stop offset="1" stopColor="#26D9FF" />
            </linearGradient>
            <linearGradient id="nfl2" x1="0" y1="0" x2="1" y2="0">
              <stop offset="0" stopColor="#F59E0B" />
              <stop offset="1" stopColor="#3B82F6" />
            </linearGradient>
            <linearGradient id="nfl3" x1="1" y1="0" x2="0" y2="0">
              <stop offset="0" stopColor="#A855F7" />
              <stop offset="1" stopColor="#3B82F6" />
            </linearGradient>
          </defs>
          <path d="M320,118 L320,300" stroke="url(#nfl1)" strokeWidth="2.5" fill="none" strokeDasharray="8 8" style={{ animation: "nfDash 4s linear infinite" }} />
          <path d="M132,268 C200,300 240,330 300,360" stroke="url(#nfl2)" strokeWidth="2.5" fill="none" strokeDasharray="8 8" style={{ animation: "nfDash 5s linear infinite" }} />
          <path d="M508,268 C440,300 400,330 340,360" stroke="url(#nfl3)" strokeWidth="2.5" fill="none" strokeDasharray="8 8" style={{ animation: "nfDash 4.5s linear infinite" }} />
          <path d="M150,635 C210,608 255,580 300,545" stroke="rgba(236,72,153,.7)" strokeWidth="2.5" fill="none" strokeDasharray="8 8" style={{ animation: "nfDash 5.5s linear infinite" }} />
          <path d="M490,635 C430,608 385,580 340,545" stroke="rgba(92,169,255,.7)" strokeWidth="2.5" fill="none" strokeDasharray="8 8" style={{ animation: "nfDash 4.2s linear infinite" }} />
          <path d="M320,600 L320,800" stroke="rgba(92,169,255,.7)" strokeWidth="2.5" fill="none" strokeDasharray="8 8" style={{ animation: "nfDash 4s linear infinite" }} />
        </svg>

        {/* central command center */}
        <div
          className="absolute left-1/2 top-[295px] w-[320px] -translate-x-1/2 rounded-[28px] border-[1.5px] border-white/20 bg-white/10 px-[22px] pb-[18px] pt-[22px] backdrop-blur-2xl"
          style={{ animation: "nfGlow 6s ease-in-out infinite", zIndex: 3 }}
        >
          <div className="flex items-center justify-between gap-2.5">
            <span
              className="text-[15px] font-bold leading-tight text-white"
              style={{ fontFamily: "var(--font-sora)" }}
            >
              NidhiFlow AI
              <br />
              Command Center
            </span>
            <span className="inline-flex items-center gap-1.5 rounded-full bg-[#4ADE80]/15 px-2.5 py-1 text-[11.5px] font-bold text-[#86EFAC]">
              <span
                className="h-[7px] w-[7px] rounded-full bg-[#4ADE80] shadow-[0_0_8px_#4ADE80]"
                style={{ animation: "nfPulse 2s ease-in-out infinite" }}
              />
              System Online
            </span>
          </div>
          <div className="relative flex justify-center py-4">
            <span className="absolute left-1/2 top-1/2 h-24 w-24 -translate-x-1/2 -translate-y-1/2 rounded-full border-2 border-[#26D9FF]/50" style={{ animation: "nfRing 2.6s ease-out infinite" }} />
            <span className="absolute left-1/2 top-1/2 h-24 w-24 -translate-x-1/2 -translate-y-1/2 rounded-full border-2 border-[#A855F7]/40" style={{ animation: "nfRing 2.6s ease-out 1.3s infinite" }} />
            <Image
              src={LOGO_URL}
              alt=""
              width={84}
              height={84}
              className="object-contain drop-shadow-[0_0_18px_rgba(38,217,255,0.6)]"
              style={{ animation: "nfFloat 5s ease-in-out infinite" }}
            />
          </div>
          <div className="grid grid-cols-2 gap-2.5">
            <div className="rounded-2xl border border-white/15 bg-white/10 px-3.5 py-2.5">
              <div className="text-[10.5px] font-bold uppercase tracking-wide text-[#67E8F9]">Total Applications</div>
              <div className="mt-1 text-[20px] font-extrabold text-white" style={{ fontFamily: "var(--font-sora)" }}>
                12,842
              </div>
              <div className="text-[10.5px] font-bold text-[#86EFAC]">▲ 18% vs last 30 days</div>
            </div>
            <div className="rounded-2xl border border-white/15 bg-white/10 px-3.5 py-2.5">
              <div className="text-[10.5px] font-bold uppercase tracking-wide text-[#F9A8D4]">Processing</div>
              <div className="mt-1 text-[20px] font-extrabold text-white" style={{ fontFamily: "var(--font-sora)" }}>
                2,341
              </div>
              <svg width="100%" height="16" viewBox="0 0 100 16" preserveAspectRatio="none">
                <polyline points="0,13 15,10 30,12 45,7 60,9 75,4 100,6" fill="none" stroke="#26D9FF" strokeWidth="2" />
              </svg>
            </div>
          </div>
        </div>

        {/* agent cards */}
        {AGENTS.map((ag) => (
          <motion.div
            key={ag.n}
            initial={{ opacity: 0, y: 16 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5 }}
            className="nf-agent-card absolute w-[216px] rounded-[22px] border-[1.5px] border-white/20 bg-white/10 px-[17px] py-4 backdrop-blur-2xl"
            style={{ left: ag.x, top: ag.y, zIndex: 2, animation: ag.float }}
          >
            <div className="flex items-center gap-2.5">
              <span
                className="flex h-9 w-9 items-center justify-center rounded-xl text-[15px] font-extrabold text-white"
                style={{ background: ag.iconBg, boxShadow: `0 4px 14px ${ag.shadow}`, fontFamily: "var(--font-sora)" }}
              >
                {ag.n}
              </span>
              <span className="text-[14.5px] font-bold leading-tight text-white" style={{ fontFamily: "var(--font-sora)" }}>
                {ag.title}
              </span>
            </div>
            <div className="mt-2.5 text-[12.5px] font-medium leading-snug text-[#D7E4FF]">{ag.desc}</div>
          </motion.div>
        ))}

        {/* infra platform */}
        <div className="absolute left-1/2 top-[790px] h-[210px] w-[560px] -translate-x-1/2" style={{ zIndex: 2 }}>
          <svg width="560" height="210" viewBox="0 0 560 210" className="absolute inset-0">
            <defs>
              <radialGradient id="nfp1" cx="50%" cy="50%" r="50%">
                <stop offset="0" stopColor="rgba(92,169,255,.45)" />
                <stop offset="70%" stopColor="rgba(124,77,255,.18)" />
                <stop offset="1" stopColor="rgba(124,77,255,0)" />
              </radialGradient>
            </defs>
            <ellipse cx="280" cy="140" rx="260" ry="48" fill="url(#nfp1)" />
            <ellipse cx="280" cy="140" rx="240" ry="40" fill="none" stroke="rgba(38,217,255,.55)" strokeWidth="1.5" strokeDasharray="6 10" style={{ animation: "nfDash 8s linear infinite" }} />
          </svg>
          <div className="absolute inset-x-0 top-[28px] flex justify-center gap-4">
            {INFRA.map((inf) => (
              <div
                key={inf.name}
                className="w-[106px] rounded-[18px] border-[1.5px] border-white/20 bg-white/10 px-2.5 py-3.5 text-center backdrop-blur-2xl"
                style={{ boxShadow: `0 12px 30px rgba(0,0,0,.25), 0 0 24px ${inf.glow}` }}
              >
                <span
                  className="mb-2 inline-flex h-[34px] w-[34px] items-center justify-center rounded-[11px]"
                  style={{ background: inf.iconBg }}
                >
                  {inf.logo ? (
                    <Image src={inf.logo} alt="" width={18} height={18} className="object-contain" />
                  ) : (
                    inf.Icon && <inf.Icon size={18} color="#fff" strokeWidth={2.2} />
                  )}
                </span>
                <div className="text-[12px] font-extrabold text-white">{inf.name}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
