import { Navbar } from "@/components/landing/navbar";
import { HeroBackground } from "@/components/landing/hero-background";
import { Hero } from "@/components/landing/hero";
import { Metrics } from "@/components/landing/metrics";

export default function Home() {
  return (
    <main className="min-h-screen">
      <div className="relative isolate overflow-hidden bg-[#050b18]">
        <HeroBackground />
        <Navbar />
        <Hero />
      </div>
      <div className="bg-[linear-gradient(160deg,#F8FBFF_0%,#EEF6FF_25%,#F5F1FF_50%,#E8F8FF_75%,#FFF8FC_100%)]">
        <Metrics />
      </div>
    </main>
  );
}
