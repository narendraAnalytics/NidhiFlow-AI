"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { motion, AnimatePresence } from "framer-motion";
import { ArrowRight, Eye, EyeOff, Loader2, Lock, Mail } from "lucide-react";
import { toast } from "sonner";
import { cn } from "@/lib/utils";
import { friendlyAuthError, useAuth } from "@/contexts/auth-context";

const authSchema = z.object({
  email: z.email("Enter a valid email address").min(1, "Email is required"),
  password: z.string().min(6, "Password must be at least 6 characters"),
});

type AuthFormValues = z.infer<typeof authSchema>;

type Mode = "signin" | "signup";

export function AuthForm() {
  const router = useRouter();
  const { user, loading, signInEmail, signUpEmail, signInGoogle } = useAuth();
  const [mode, setMode] = useState<Mode>("signin");
  const [showPassword, setShowPassword] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [googleSubmitting, setGoogleSubmitting] = useState(false);

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<AuthFormValues>({
    resolver: zodResolver(authSchema),
  });

  useEffect(() => {
    if (!loading && user) {
      router.replace("/");
    }
  }, [loading, user, router]);

  const switchMode = (next: Mode) => {
    setMode(next);
    reset();
  };

  const onSubmit = async (values: AuthFormValues) => {
    setSubmitting(true);
    try {
      if (mode === "signin") {
        await signInEmail(values.email, values.password);
      } else {
        await signUpEmail(values.email, values.password);
      }
      router.replace("/");
    } catch (error) {
      toast.error(friendlyAuthError(error));
    } finally {
      setSubmitting(false);
    }
  };

  const onGoogle = async () => {
    setGoogleSubmitting(true);
    try {
      await signInGoogle();
      router.replace("/");
    } catch (error) {
      toast.error(friendlyAuthError(error));
    } finally {
      setGoogleSubmitting(false);
    }
  };

  const busy = submitting || googleSubmitting;

  return (
    <div className="w-full max-w-[440px] rounded-[28px] border border-white/15 bg-white/10 p-7 shadow-[0_20px_60px_rgba(0,0,0,0.35)] backdrop-blur-2xl sm:p-9">
      {/* Segmented tab toggle */}
      <div className="relative mb-7 grid grid-cols-2 rounded-2xl border border-white/15 bg-white/5 p-1">
        <motion.div
          animate={{ x: mode === "signin" ? "0%" : "100%" }}
          transition={{ type: "spring", stiffness: 400, damping: 32 }}
          className="absolute inset-y-1 left-1 w-[calc(50%-4px)] rounded-xl bg-gradient-to-r from-[#26D9FF] via-[#3B82F6] to-[#A855F7] shadow-[0_4px_16px_rgba(59,130,246,0.4)]"
        />
        <button
          type="button"
          onClick={() => switchMode("signin")}
          className={cn(
            "relative z-10 rounded-xl py-2.5 text-[14.5px] font-bold transition-colors",
            mode === "signin" ? "text-white" : "text-white/60 hover:text-white/85",
          )}
        >
          Sign In
        </button>
        <button
          type="button"
          onClick={() => switchMode("signup")}
          className={cn(
            "relative z-10 rounded-xl py-2.5 text-[14.5px] font-bold transition-colors",
            mode === "signup" ? "text-white" : "text-white/60 hover:text-white/85",
          )}
        >
          Sign Up
        </button>
      </div>

      <AnimatePresence mode="wait">
        <motion.div
          key={mode}
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -8 }}
          transition={{ duration: 0.18 }}
        >
          <h2
            className="mb-1.5 text-[22px] font-extrabold text-white"
            style={{ fontFamily: "var(--font-sora)" }}
          >
            {mode === "signin" ? "Welcome back" : "Create your account"}
          </h2>
          <p className="mb-6 text-[14px] leading-relaxed text-[#B9C7E6]">
            {mode === "signin"
              ? "Sign in to access your loan operations dashboard."
              : "Get started with intelligent loan operations."}
          </p>

          <form onSubmit={handleSubmit(onSubmit)} noValidate className="flex flex-col gap-4">
            <div>
              <label className="mb-1.5 block text-[13px] font-semibold text-white/80">
                Email address
              </label>
              <div className="relative">
                <Mail
                  size={17}
                  className="pointer-events-none absolute left-3.5 top-1/2 -translate-y-1/2 text-white/40"
                />
                <input
                  type="email"
                  autoComplete="email"
                  placeholder="you@company.com"
                  disabled={busy}
                  {...register("email")}
                  className="w-full rounded-2xl border border-white/15 bg-white/5 py-3 pl-11 pr-4 text-[14.5px] text-white placeholder:text-white/30 outline-none transition-colors focus:border-[#26D9FF]/60 focus:bg-white/10 disabled:opacity-60"
                />
              </div>
              {errors.email && (
                <p className="mt-1.5 text-[12.5px] font-medium text-[#FCA5A5]">
                  {errors.email.message}
                </p>
              )}
            </div>

            <div>
              <label className="mb-1.5 block text-[13px] font-semibold text-white/80">
                Password
              </label>
              <div className="relative">
                <Lock
                  size={17}
                  className="pointer-events-none absolute left-3.5 top-1/2 -translate-y-1/2 text-white/40"
                />
                <input
                  type={showPassword ? "text" : "password"}
                  autoComplete={mode === "signin" ? "current-password" : "new-password"}
                  placeholder="••••••••"
                  disabled={busy}
                  {...register("password")}
                  className="w-full rounded-2xl border border-white/15 bg-white/5 py-3 pl-11 pr-11 text-[14.5px] text-white placeholder:text-white/30 outline-none transition-colors focus:border-[#26D9FF]/60 focus:bg-white/10 disabled:opacity-60"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword((v) => !v)}
                  aria-label={showPassword ? "Hide password" : "Show password"}
                  className="absolute right-3.5 top-1/2 -translate-y-1/2 text-white/40 hover:text-white/70"
                >
                  {showPassword ? <EyeOff size={17} /> : <Eye size={17} />}
                </button>
              </div>
              {errors.password && (
                <p className="mt-1.5 text-[12.5px] font-medium text-[#FCA5A5]">
                  {errors.password.message}
                </p>
              )}
            </div>

            <button
              type="submit"
              disabled={busy}
              className="nf-cta mt-1 inline-flex items-center justify-center gap-2 rounded-2xl bg-gradient-to-r from-[#26D9FF] via-[#3B82F6] to-[#A855F7] py-3.5 text-[15px] font-extrabold text-white shadow-[0_10px_30px_rgba(59,130,246,0.4)] transition-all disabled:cursor-not-allowed disabled:opacity-70"
            >
              {submitting ? (
                <Loader2 size={18} className="animate-spin" />
              ) : (
                <>
                  {mode === "signin" ? "Sign In" : "Create Account"}
                  <ArrowRight size={17} />
                </>
              )}
            </button>
          </form>

          <div className="my-6 flex items-center gap-3">
            <div className="h-px flex-1 bg-white/15" />
            <span className="text-[12.5px] font-semibold text-white/40">or continue with</span>
            <div className="h-px flex-1 bg-white/15" />
          </div>

          <button
            type="button"
            onClick={onGoogle}
            disabled={busy}
            className="inline-flex w-full items-center justify-center gap-3 rounded-2xl border border-white/20 bg-white/95 py-3 text-[14.5px] font-bold text-[#1F2937] shadow-[0_6px_20px_rgba(0,0,0,0.15)] transition-transform hover:scale-[1.01] disabled:cursor-not-allowed disabled:opacity-70"
          >
            {googleSubmitting ? (
              <Loader2 size={18} className="animate-spin" />
            ) : (
              <>
                <GoogleGlyph />
                Continue with Google
              </>
            )}
          </button>

          <p className="mt-6 text-center text-[13px] text-white/50">
            {mode === "signin" ? (
              <>
                Don&apos;t have an account?{" "}
                <button
                  type="button"
                  onClick={() => switchMode("signup")}
                  className="font-bold text-[#7DD8FF] hover:text-[#A5E6FF]"
                >
                  Sign up
                </button>
              </>
            ) : (
              <>
                Already have an account?{" "}
                <button
                  type="button"
                  onClick={() => switchMode("signin")}
                  className="font-bold text-[#7DD8FF] hover:text-[#A5E6FF]"
                >
                  Sign in
                </button>
              </>
            )}
          </p>
        </motion.div>
      </AnimatePresence>
    </div>
  );
}

function GoogleGlyph() {
  return (
    <svg width="18" height="18" viewBox="0 0 48 48" aria-hidden="true">
      <path
        fill="#FFC107"
        d="M43.6 20.5H42V20H24v8h11.3c-1.6 4.7-6.1 8-11.3 8-6.6 0-12-5.4-12-12s5.4-12 12-12c3.1 0 5.9 1.2 8 3.1l5.7-5.7C34.6 6.1 29.6 4 24 4 12.9 4 4 12.9 4 24s8.9 20 20 20 20-8.9 20-20c0-1.3-.1-2.7-.4-3.5z"
      />
      <path
        fill="#FF3D00"
        d="M6.3 14.7l6.6 4.8C14.6 15.9 18.9 13 24 13c3.1 0 5.9 1.2 8 3.1l5.7-5.7C34.6 6.1 29.6 4 24 4 16.3 4 9.7 8.3 6.3 14.7z"
      />
      <path
        fill="#4CAF50"
        d="M24 44c5.5 0 10.4-2.1 14.1-5.6l-6.5-5.5C29.6 34.7 26.9 36 24 36c-5.2 0-9.6-3.3-11.3-7.9l-6.5 5C9.6 39.6 16.3 44 24 44z"
      />
      <path
        fill="#1976D2"
        d="M43.6 20.5H42V20H24v8h11.3c-.8 2.3-2.2 4.2-4.1 5.6l6.5 5.5C40.7 36.9 44 31 44 24c0-1.3-.1-2.7-.4-3.5z"
      />
    </svg>
  );
}
