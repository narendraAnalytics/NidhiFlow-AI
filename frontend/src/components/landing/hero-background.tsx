import Image from "next/image";

const BANNER_URL =
  "https://res.cloudinary.com/dkqbzwicr/image/upload/v1784610404/nidhiflowbannerImage_hbnvcf.png";

export function HeroBackground() {
  return (
    <div className="pointer-events-none absolute inset-0 overflow-hidden">
      <Image
        src={BANNER_URL}
        alt=""
        fill
        priority
        unoptimized
        className="object-cover object-center"
      />
      {/* Dark overlay so the photo reads as ambient texture, not a bright wash */}
      <div className="absolute inset-0 bg-gradient-to-b from-[#050b18]/70 via-[#0b1226]/60 to-[#050b18]/85" />

      {/* Layered aurora accents on top of the photo, for depth */}
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
  );
}
