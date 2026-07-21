import type { Metadata } from "next";
import Image from "next/image";
import Link from "next/link";
import { Check, ShieldCheck } from "lucide-react";
import { AuthForm } from "@/components/auth/auth-form";

const LOGO_URL =
  "https://res.cloudinary.com/dkqbzwicr/image/upload/v1784610412/LogoNidhiFlowAI_wqxhyg.png";

export const metadata: Metadata = {
  title: "Sign In — NidhiFlow AI",
  description: "Sign in or create an account to access NidhiFlow AI's loan operations platform.",
};

const TRUST_POINTS = [
  "Human-in-the-loop lending decisions",
  "Designed using principles from the RBI Digital Lending Directions, 2025",
  "Enterprise-grade document intake, validation and audit trail",
];

export default function AuthPage() {
  return (
    <main className="relative isolate min-h-screen overflow-hidden bg-[#050b18]">
      {/* Aurora background, consistent with the landing hero */}
      <div className="pointer-events-none absolute inset-0 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-b from-[#050b18] via-[#0b1226] to-[#050b18]" />
        <div
          className="absolute -left-32 -top-44 h-[640px] w-[640px] rounded-full opacity-40 blur-[70px]"
          style={{
            background:
              "radial-gradient(circle at 40% 40%, rgba(38,217,255,0.5) 0%, rgba(38,217,255,0) 65%)",
            animation: "nfAurora 18s ease-in-out infinite",
          }}
        />
        <div
          className="absolute -right-40 -top-28 h-[720px] w-[720px] rounded-full opacity-40 blur-[80px]"
          style={{
            background:
              "radial-gradient(circle at 55% 45%, rgba(168,85,247,0.5) 0%, rgba(168,85,247,0) 65%)",
            animation: "nfAurora2 22s ease-in-out infinite",
          }}
        />
        <div
          className="absolute bottom-0 left-1/4 h-[520px] w-[520px] rounded-full opacity-30 blur-[70px]"
          style={{
            background:
              "radial-gradient(circle, rgba(236,72,153,0.5) 0%, rgba(236,72,153,0) 65%)",
            animation: "nfAurora2 20s ease-in-out infinite",
          }}
        />
      </div>

      <div className="relative z-10 mx-auto flex min-h-screen max-w-[1240px] flex-wrap items-center gap-14 px-6 py-12">
        {/* Left: brand panel */}
        <div className="flex min-w-[300px] flex-1 basis-[440px] flex-col items-start gap-8">
          <Link href="/" className="flex items-center gap-2.5">
            <Image
              src={LOGO_URL}
              alt="NidhiFlow AI"
              width={40}
              height={40}
              priority
              unoptimized
              className="object-contain drop-shadow-[0_2px_8px_rgba(124,77,255,0.45)]"
            />
            <span
              className="text-[19px] font-extrabold tracking-tight text-white"
              style={{ fontFamily: "var(--font-sora)" }}
            >
              NidhiFlow{" "}
              <span className="bg-gradient-to-r from-[#26D9FF] to-[#7C4DFF] bg-clip-text text-transparent">
                AI
              </span>
            </span>
          </Link>

          <div className="inline-flex items-center gap-2 rounded-full border border-white/25 bg-white/10 px-[18px] py-2 text-[13.5px] font-bold text-[#FCD34D] backdrop-blur-xl">
            <ShieldCheck size={17} color="#FCD34D" />
            Enterprise Agentic Loan Operations
          </div>

          <h1
            className="m-0 text-[clamp(30px,4vw,44px)] font-extrabold leading-[1.12] tracking-tight text-white"
            style={{ fontFamily: "var(--font-sora)", textWrap: "balance" }}
          >
            One platform for your entire{" "}
            <span
              className="bg-clip-text text-transparent"
              style={{
                backgroundImage:
                  "linear-gradient(92deg, #26D9FF 0%, #3B82F6 35%, #7C4DFF 65%, #EC4899 100%)",
              }}
            >
              loan operations lifecycle.
            </span>
          </h1>

          <p
            className="m-0 max-w-[460px] text-[15.5px] leading-[1.7] text-[#D7E4FF]"
            style={{ textWrap: "pretty" }}
          >
            Sign in to manage document intake, validation, pipelines,
            monitoring and audit — all in one place.
          </p>

          <div className="flex flex-col gap-3">
            {TRUST_POINTS.map((point) => (
              <span
                key={point}
                className="inline-flex items-start gap-2 text-[13.5px] font-semibold text-[#86EFAC]"
              >
                <Check size={16} strokeWidth={2.6} className="mt-0.5 shrink-0" />
                {point}
              </span>
            ))}
          </div>
        </div>

        {/* Right: auth form */}
        <div className="flex min-w-[320px] flex-1 basis-[440px] items-center justify-center">
          <AuthForm />
        </div>
      </div>
    </main>
  );
}
