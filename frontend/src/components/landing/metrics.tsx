"use client";

import { motion } from "framer-motion";
import { TrendingUp, ShieldCheck, Users, FileStack } from "lucide-react";

const METRICS = [
  {
    value: "90%",
    label: "Faster Processing",
    sub: "than traditional methods",
    iconBg: "linear-gradient(135deg,#26D9FF,#3B82F6)",
    glow: "rgba(38,217,255,.35)",
    tint: "rgba(38,217,255,.08)",
    textColor: "var(--bright-cyan-on-light)",
    Icon: TrendingUp,
  },
  {
    value: "99.9%",
    label: "System Uptime",
    sub: "enterprise-grade reliability",
    iconBg: "linear-gradient(135deg,#22C55E,#16A34A)",
    glow: "rgba(34,197,94,.35)",
    tint: "rgba(34,197,94,.08)",
    textColor: "var(--bright-mint-on-light)",
    Icon: ShieldCheck,
  },
  {
    value: "500+",
    label: "Financial Institutions",
    sub: "trust NidhiFlow AI",
    iconBg: "linear-gradient(135deg,#F59E0B,#F97316)",
    glow: "rgba(245,158,11,.35)",
    tint: "rgba(245,158,11,.08)",
    textColor: "var(--bright-amber-on-light)",
    Icon: Users,
  },
  {
    value: "10M+",
    label: "Applications Processed",
    sub: "and counting",
    iconBg: "linear-gradient(135deg,#EC4899,#DB2777)",
    glow: "rgba(236,72,153,.35)",
    tint: "rgba(236,72,153,.08)",
    textColor: "var(--bright-rose-on-light)",
    Icon: FileStack,
  },
];

export function Metrics() {
  return (
    <div className="relative z-10 mx-auto max-w-[1240px] px-6 pb-10 pt-4">
      <div className="grid grid-cols-1 gap-3 rounded-[28px] border-[1.5px] border-white/70 bg-white/60 p-4 shadow-[0_20px_56px_rgba(59,130,246,0.14)] backdrop-blur-2xl sm:grid-cols-2 lg:grid-cols-4">
        {METRICS.map((m, i) => (
          <motion.div
            key={m.label}
            initial={{ opacity: 0, y: 16 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.4, delay: i * 0.08 }}
            className="nf-metric flex items-center gap-2 rounded-[20px] border border-white/90 p-4 transition-transform"
            style={{ background: `linear-gradient(135deg, rgba(255,255,255,.85), ${m.tint})` }}
          >
            <span
              className="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-2xl"
              style={{ background: m.iconBg, boxShadow: `0 6px 18px ${m.glow}` }}
            >
              <m.Icon size={18} color="#fff" strokeWidth={2.1} />
            </span>
            <div>
              <div
                className="text-[26px] font-extrabold tracking-tight"
                style={{ fontFamily: "var(--font-sora)", color: m.textColor }}
              >
                {m.value}
              </div>
              <div className="text-[13px] font-bold" style={{ color: m.textColor }}>
                {m.label}
              </div>
              <div className="text-[11.5px] font-semibold text-[#8A97B8]">{m.sub}</div>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );
}
