"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Loader2, Send } from "lucide-react";
import { toast } from "sonner";
import { useAuth } from "@/contexts/auth-context";
import { createCustomer, createLoanApplication } from "@/lib/api";
import { DocumentUploadSection } from "./document-upload-section";

type Phase = "form" | "documents" | "done";

const loanApplicationSchema = z.object({
  full_name: z.string().min(1, "Full name is required"),
  email: z.email("Enter a valid email address").min(1, "Email is required"),
  phone: z.string().min(1, "Phone is required"),
  pan: z.string().min(1, "PAN is required"),
  aadhaar: z.string().min(1, "Aadhaar is required"),
  address: z.string().optional(),
  loan_type: z.enum(["Home", "Personal", "Business"]),
  requested_amount: z.string().min(1, "Requested amount is required"),
  loan_purpose: z.string().optional(),
  employment_type: z.string().optional(),
  monthly_income: z.string().optional(),
  employer: z.string().optional(),
  tenure: z.string().optional(),
  interest_rate: z.string().optional(),
  branch: z.string().optional(),
});

type LoanApplicationFormValues = z.infer<typeof loanApplicationSchema>;

const inputClass =
  "w-full rounded-2xl border border-white/15 bg-white/5 py-3 px-4 text-[14.5px] text-white placeholder:text-white/30 outline-none transition-colors focus:border-[#26D9FF]/60 focus:bg-white/10 disabled:opacity-60";
const labelClass = "mb-1.5 block text-[13px] font-semibold text-white/80";
const errorClass = "mt-1.5 text-[12.5px] font-medium text-[#FCA5A5]";

export default function LoanApplicationPage() {
  const { user, loading } = useAuth();
  const router = useRouter();
  const [submitting, setSubmitting] = useState(false);
  const [phase, setPhase] = useState<Phase>("form");
  const [loanId, setLoanId] = useState<string | null>(null);

  useEffect(() => {
    if (!loading && !user) {
      router.replace("/auth");
    }
  }, [loading, user, router]);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoanApplicationFormValues>({
    resolver: zodResolver(loanApplicationSchema),
  });

  if (loading || !user) {
    return null;
  }

  const onSubmit = async (values: LoanApplicationFormValues) => {
    setSubmitting(true);
    try {
      const idToken = await user.getIdToken();
      const customer = await createCustomer(
        {
          full_name: values.full_name,
          email: values.email,
          phone: values.phone,
          pan: values.pan,
          aadhaar: values.aadhaar,
          address: values.address,
        },
        idToken,
      );
      const loanApplication = await createLoanApplication(
        {
          customer_id: customer.id,
          loan_type: values.loan_type,
          requested_amount: Number(values.requested_amount),
          loan_purpose: values.loan_purpose,
          employment_type: values.employment_type,
          monthly_income: values.monthly_income ? Number(values.monthly_income) : undefined,
          employer: values.employer,
          tenure: values.tenure ? Number(values.tenure) : undefined,
          interest_rate: values.interest_rate ? Number(values.interest_rate) : undefined,
          branch: values.branch,
        },
        idToken,
      );
      setLoanId(loanApplication.id);
      setPhase("documents");
      toast.success("Loan application created — now add supporting documents.");
    } catch {
      toast.error("Submission failed. Please try again.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <main className="flex min-h-screen items-center justify-center bg-[#050b18] px-6 py-16">
      <div className="w-full max-w-[640px] rounded-[28px] border border-white/15 bg-white/10 p-8 shadow-[0_20px_60px_rgba(0,0,0,0.35)] backdrop-blur-2xl">
        <h1
          className="mb-1.5 text-[22px] font-extrabold text-white"
          style={{ fontFamily: "var(--font-sora)" }}
        >
          Loan Application
        </h1>
        <p className="mb-6 text-[13.5px] leading-relaxed text-white/50">
          {phase === "form" &&
            "Enter customer and loan details, then upload supporting documents."}
          {phase === "documents" && "Add at least one document, then submit the application."}
          {phase === "done" && "Your application has been submitted for processing."}
        </p>

        {phase === "documents" && loanId && (
          <DocumentUploadSection loanId={loanId} onSubmitted={() => setPhase("done")} />
        )}

        {phase === "done" && (
          <button
            type="button"
            onClick={() => router.push("/dashboard")}
            className="nf-cta inline-flex items-center justify-center gap-2 rounded-2xl bg-gradient-to-r from-[#26D9FF] via-[#3B82F6] to-[#A855F7] py-3.5 text-[15px] font-extrabold text-white shadow-[0_10px_30px_rgba(59,130,246,0.4)] transition-all"
          >
            Go to dashboard
          </button>
        )}

        {phase === "form" && (
        <form onSubmit={handleSubmit(onSubmit)} noValidate className="flex flex-col gap-5">
          <div>
            <h2 className="mb-3 text-[14px] font-bold text-white/90">Customer details</h2>
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <div>
                <label className={labelClass}>Full name</label>
                <input disabled={submitting} {...register("full_name")} className={inputClass} />
                {errors.full_name && <p className={errorClass}>{errors.full_name.message}</p>}
              </div>
              <div>
                <label className={labelClass}>Email</label>
                <input
                  type="email"
                  disabled={submitting}
                  {...register("email")}
                  className={inputClass}
                />
                {errors.email && <p className={errorClass}>{errors.email.message}</p>}
              </div>
              <div>
                <label className={labelClass}>Phone</label>
                <input disabled={submitting} {...register("phone")} className={inputClass} />
                {errors.phone && <p className={errorClass}>{errors.phone.message}</p>}
              </div>
              <div>
                <label className={labelClass}>PAN</label>
                <input disabled={submitting} {...register("pan")} className={inputClass} />
                {errors.pan && <p className={errorClass}>{errors.pan.message}</p>}
              </div>
              <div>
                <label className={labelClass}>Aadhaar</label>
                <input disabled={submitting} {...register("aadhaar")} className={inputClass} />
                {errors.aadhaar && <p className={errorClass}>{errors.aadhaar.message}</p>}
              </div>
              <div>
                <label className={labelClass}>Address</label>
                <input disabled={submitting} {...register("address")} className={inputClass} />
              </div>
            </div>
          </div>

          <div>
            <h2 className="mb-3 text-[14px] font-bold text-white/90">Loan details</h2>
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <div>
                <label className={labelClass}>Loan type</label>
                <select
                  disabled={submitting}
                  {...register("loan_type")}
                  className={inputClass}
                  defaultValue="Home"
                >
                  <option value="Home">Home</option>
                  <option value="Personal">Personal</option>
                  <option value="Business">Business</option>
                </select>
                {errors.loan_type && <p className={errorClass}>{errors.loan_type.message}</p>}
              </div>
              <div>
                <label className={labelClass}>Requested amount</label>
                <input
                  type="number"
                  step="0.01"
                  disabled={submitting}
                  {...register("requested_amount")}
                  className={inputClass}
                />
                {errors.requested_amount && (
                  <p className={errorClass}>{errors.requested_amount.message}</p>
                )}
              </div>
              <div>
                <label className={labelClass}>Loan purpose</label>
                <input disabled={submitting} {...register("loan_purpose")} className={inputClass} />
              </div>
              <div>
                <label className={labelClass}>Employment type</label>
                <input
                  disabled={submitting}
                  {...register("employment_type")}
                  className={inputClass}
                />
              </div>
              <div>
                <label className={labelClass}>Monthly income</label>
                <input
                  type="number"
                  step="0.01"
                  disabled={submitting}
                  {...register("monthly_income")}
                  className={inputClass}
                />
              </div>
              <div>
                <label className={labelClass}>Employer</label>
                <input disabled={submitting} {...register("employer")} className={inputClass} />
              </div>
              <div>
                <label className={labelClass}>Tenure (months)</label>
                <input
                  type="number"
                  disabled={submitting}
                  {...register("tenure")}
                  className={inputClass}
                />
              </div>
              <div>
                <label className={labelClass}>Interest rate (%)</label>
                <input
                  type="number"
                  step="0.01"
                  disabled={submitting}
                  {...register("interest_rate")}
                  className={inputClass}
                />
              </div>
              <div>
                <label className={labelClass}>Branch</label>
                <input disabled={submitting} {...register("branch")} className={inputClass} />
              </div>
            </div>
          </div>

          <button
            type="submit"
            disabled={submitting}
            className="nf-cta mt-2 inline-flex items-center justify-center gap-2 rounded-2xl bg-gradient-to-r from-[#26D9FF] via-[#3B82F6] to-[#A855F7] py-3.5 text-[15px] font-extrabold text-white shadow-[0_10px_30px_rgba(59,130,246,0.4)] transition-all disabled:cursor-not-allowed disabled:opacity-70"
          >
            {submitting ? (
              <Loader2 size={18} className="animate-spin" />
            ) : (
              <>
                Submit application
                <Send size={17} />
              </>
            )}
          </button>
        </form>
        )}
      </div>
    </main>
  );
}
