"use client";

import { useEffect, useState } from "react";
import Image from "next/image";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import {
  ArrowLeft,
  CheckCircle2,
  Landmark,
  Loader2,
  Send,
  User as UserIcon,
} from "lucide-react";
import { toast } from "sonner";
import { useAuth } from "@/contexts/auth-context";
import { createCustomer, createLoanApplication } from "@/lib/api";
import { DocumentUploadSection } from "./document-upload-section";

const LOGO_URL =
  "https://res.cloudinary.com/dkqbzwicr/image/upload/v1784610412/LogoNidhiFlowAI_wqxhyg.png";

type Phase = "form" | "documents" | "done";

const loanApplicationSchema = z.object({
  full_name: z.string().min(1, "Full name is required"),
  email: z.email("Enter a valid email address").min(1, "Email is required"),
  phone: z.string().min(1, "Phone is required"),
  pan: z.string().min(1, "PAN is required"),
  aadhaar: z.string().min(1, "Aadhaar is required"),
  address: z.string().optional(),
  age: z.string().optional(),
  city: z.string().optional(),
  loan_type: z.enum(["Home", "Personal", "Business"]),
  requested_amount: z.string().min(1, "Requested amount is required"),
  loan_purpose: z.string().optional(),
  employment_type: z.string().optional(),
  monthly_income: z.string().optional(),
  employer: z.string().optional(),
  tenure: z.string().optional(),
  interest_rate: z.string().optional(),
  branch: z.string().optional(),
  credit_score: z.string().optional(),
  existing_emi: z.string().optional(),
  property_value: z.string().optional(),
  down_payment: z.string().optional(),
  employment_experience_years: z.string().optional(),
  existing_loan_outstanding: z.string().optional(),
  bank_name: z.string().optional(),
  monthly_household_expenses: z.string().optional(),
});

type LoanApplicationFormValues = z.infer<typeof loanApplicationSchema>;

const EMPLOYMENT_TYPES = [
  "Salaried",
  "Self-employed",
  "Business Owner",
  "Professional",
  "Government Employee",
];

const PERSONAL_LOAN_PURPOSES = [
  "Medical Emergency",
  "Education",
  "Wedding",
  "Home Renovation",
  "Travel",
  "Debt Consolidation",
  "Consumer Durable Purchase",
  "Business Requirement",
  "Personal Expenses",
  "Other",
];

export const inputClass =
  "w-full rounded-xl border border-[#e2e8f5] bg-white py-3 px-4 text-[14.5px] text-[#0f1b33] placeholder:text-[#9aa8c2] outline-none transition-colors focus:border-[#3B82F6] focus:ring-2 focus:ring-[#3B82F6]/20 disabled:opacity-60 disabled:bg-[#f8fbff]";
export const labelClass = "mb-1.5 block text-[13px] font-semibold text-[#0f1b33]";
const errorClass = "mt-1.5 text-[12.5px] font-medium text-[#be185d]";

const STEPS: { key: Phase; label: string }[] = [
  { key: "form", label: "Details" },
  { key: "documents", label: "Documents" },
  { key: "done", label: "Done" },
];

function StepIndicator({ phase }: { phase: Phase }) {
  const activeIndex = STEPS.findIndex((s) => s.key === phase);
  return (
    <div className="mb-7 flex items-center">
      {STEPS.map((step, i) => {
        const isComplete = i < activeIndex;
        const isActive = i === activeIndex;
        return (
          <div key={step.key} className="flex flex-1 items-center last:flex-none">
            <div className="flex flex-col items-center gap-1.5">
              <div
                className={
                  "flex h-8 w-8 items-center justify-center rounded-full text-[12.5px] font-bold transition-colors " +
                  (isComplete || isActive
                    ? "bg-gradient-to-r from-[#26D9FF] via-[#3B82F6] to-[#A855F7] text-white shadow-[0_6px_16px_rgba(59,130,246,0.35)]"
                    : "border border-[#e2e8f5] bg-white text-[#9aa8c2]")
                }
              >
                {isComplete ? <CheckCircle2 size={16} /> : i + 1}
              </div>
              <span
                className={
                  "text-[11.5px] font-semibold " +
                  (isActive || isComplete ? "text-[#0f1b33]" : "text-[#9aa8c2]")
                }
              >
                {step.label}
              </span>
            </div>
            {i < STEPS.length - 1 && (
              <div
                className={
                  "mx-2 mb-5 h-[2px] flex-1 rounded-full transition-colors " +
                  (isComplete ? "bg-gradient-to-r from-[#26D9FF] to-[#A855F7]" : "bg-[#e2e8f5]")
                }
              />
            )}
          </div>
        );
      })}
    </div>
  );
}

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
    watch,
    formState: { errors },
  } = useForm<LoanApplicationFormValues>({
    resolver: zodResolver(loanApplicationSchema),
    defaultValues: { loan_type: "Home" },
  });

  const selectedLoanType = watch("loan_type");
  const isPersonal = selectedLoanType === "Personal";

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
          age: values.age ? Number(values.age) : undefined,
          city: values.city,
        },
        idToken,
      );
      const isPersonalLoan = values.loan_type === "Personal";
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
          credit_score: values.credit_score ? Number(values.credit_score) : undefined,
          existing_emi: values.existing_emi ? Number(values.existing_emi) : undefined,
          property_value:
            !isPersonalLoan && values.property_value ? Number(values.property_value) : undefined,
          down_payment:
            !isPersonalLoan && values.down_payment ? Number(values.down_payment) : undefined,
          employment_experience_years:
            isPersonalLoan && values.employment_experience_years
              ? Number(values.employment_experience_years)
              : undefined,
          existing_loan_outstanding:
            isPersonalLoan && values.existing_loan_outstanding
              ? Number(values.existing_loan_outstanding)
              : undefined,
          bank_name: isPersonalLoan ? values.bank_name : undefined,
          monthly_household_expenses:
            isPersonalLoan && values.monthly_household_expenses
              ? Number(values.monthly_household_expenses)
              : undefined,
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
    <main className="relative min-h-screen overflow-hidden bg-[#f8fbff] px-6 py-16">
      <div className="pointer-events-none absolute -left-32 -top-32 h-[420px] w-[420px] rounded-full bg-[#EAFBFF] blur-3xl" />
      <div className="pointer-events-none absolute right-[-10%] top-40 h-[380px] w-[380px] rounded-full bg-[#F5F1FF] blur-3xl" />
      <div className="pointer-events-none absolute bottom-[-15%] left-1/3 h-[420px] w-[420px] rounded-full bg-[#FFF8FC] blur-3xl" />

      <div className="relative mx-auto flex w-full max-w-[1100px] flex-col">
        <Link href="/" className="mb-6 flex justify-center">
          <Image
            src={LOGO_URL}
            alt="NidhiFlow AI"
            width={56}
            height={56}
            priority
            unoptimized
            className="object-contain drop-shadow-[0_2px_8px_rgba(124,77,255,0.25)]"
          />
        </Link>

        <Link
          href="/dashboard"
          className="mb-5 inline-flex w-fit items-center gap-1.5 text-[13px] font-semibold text-[#5b6b8c] transition-colors hover:text-[#0f1b33]"
        >
          <ArrowLeft size={16} />
          Back to Dashboard
        </Link>

        <div className="rounded-[28px] border border-white/60 bg-white/75 p-8 shadow-[0_8px_30px_rgba(15,27,51,0.06)] backdrop-blur-xl">
          <h1
            className="mb-1.5 text-[22px] font-extrabold text-[#0f1b33]"
            style={{ fontFamily: "var(--font-sora)" }}
          >
            Loan Application
          </h1>
          <p className="mb-6 text-[13.5px] leading-relaxed text-[#5b6b8c]">
            {phase === "form" &&
              "Enter customer and loan details, then upload supporting documents."}
            {phase === "documents" && "Add at least one document, then submit the application."}
            {phase === "done" && "Your application has been submitted for processing."}
          </p>

          <StepIndicator phase={phase} />

          {phase === "documents" && loanId && (
            <DocumentUploadSection loanId={loanId} onSubmitted={() => setPhase("done")} />
          )}

          {phase === "done" && (
            <button
              type="button"
              onClick={() => router.push("/dashboard")}
              className="nf-cta inline-flex w-full items-center justify-center gap-2 rounded-2xl bg-gradient-to-r from-[#26D9FF] via-[#3B82F6] to-[#A855F7] py-3.5 text-[15px] font-extrabold text-white shadow-[0_10px_30px_rgba(59,130,246,0.4)] transition-all"
            >
              Go to dashboard
            </button>
          )}

          {phase === "form" && (
            <form onSubmit={handleSubmit(onSubmit)} noValidate className="flex flex-col gap-5">
              <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
                <div className="rounded-2xl border border-[#e2e8f5] bg-[#f8fbff]/60 p-5">
                  <h2 className="mb-4 flex items-center gap-2 text-[14px] font-bold text-[#0f1b33]">
                    <UserIcon size={16} className="text-[#3B82F6]" />
                    Customer details
                  </h2>
                  <div className="flex flex-col gap-4">
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
                    <div>
                      <label className={labelClass}>Age</label>
                      <input
                        type="number"
                        disabled={submitting}
                        {...register("age")}
                        className={inputClass}
                      />
                    </div>
                    <div>
                      <label className={labelClass}>City</label>
                      <input disabled={submitting} {...register("city")} className={inputClass} />
                    </div>
                  </div>
                </div>

                <div className="rounded-2xl border border-[#e2e8f5] bg-[#f8fbff]/60 p-5">
                  <h2 className="mb-4 flex items-center gap-2 text-[14px] font-bold text-[#0f1b33]">
                    <Landmark size={16} className="text-[#3B82F6]" />
                    Loan details
                  </h2>
                  <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                    <div>
                      <label className={labelClass}>Loan type</label>
                      <select
                        disabled={submitting}
                        {...register("loan_type")}
                        className={inputClass}
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
                      {isPersonal ? (
                        <select
                          disabled={submitting}
                          {...register("loan_purpose")}
                          className={inputClass}
                          defaultValue=""
                        >
                          <option value="" disabled>
                            Select purpose
                          </option>
                          {PERSONAL_LOAN_PURPOSES.map((purpose) => (
                            <option key={purpose} value={purpose}>
                              {purpose}
                            </option>
                          ))}
                        </select>
                      ) : (
                        <input
                          disabled={submitting}
                          {...register("loan_purpose")}
                          className={inputClass}
                        />
                      )}
                    </div>
                    <div>
                      <label className={labelClass}>Employment type</label>
                      <select
                        disabled={submitting}
                        {...register("employment_type")}
                        className={inputClass}
                        defaultValue=""
                      >
                        <option value="" disabled>
                          Select employment type
                        </option>
                        {EMPLOYMENT_TYPES.map((type) => (
                          <option key={type} value={type}>
                            {type}
                          </option>
                        ))}
                      </select>
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
                    <div>
                      <label className={labelClass}>Credit score (CIBIL)</label>
                      <input
                        type="number"
                        disabled={submitting}
                        {...register("credit_score")}
                        className={inputClass}
                      />
                    </div>
                    <div>
                      <label className={labelClass}>Existing EMI</label>
                      <input
                        type="number"
                        step="0.01"
                        disabled={submitting}
                        {...register("existing_emi")}
                        className={inputClass}
                      />
                    </div>
                    {!isPersonal && (
                      <>
                        <div>
                          <label className={labelClass}>Property value</label>
                          <input
                            type="number"
                            step="0.01"
                            disabled={submitting}
                            {...register("property_value")}
                            className={inputClass}
                          />
                        </div>
                        <div>
                          <label className={labelClass}>Down payment</label>
                          <input
                            type="number"
                            step="0.01"
                            disabled={submitting}
                            {...register("down_payment")}
                            className={inputClass}
                          />
                        </div>
                      </>
                    )}
                    {isPersonal && (
                      <>
                        <div>
                          <label className={labelClass}>Employment experience (years)</label>
                          <input
                            type="number"
                            disabled={submitting}
                            {...register("employment_experience_years")}
                            className={inputClass}
                          />
                        </div>
                        <div>
                          <label className={labelClass}>Existing loan outstanding</label>
                          <input
                            type="number"
                            step="0.01"
                            disabled={submitting}
                            {...register("existing_loan_outstanding")}
                            className={inputClass}
                          />
                        </div>
                        <div>
                          <label className={labelClass}>Salary account bank</label>
                          <input
                            disabled={submitting}
                            {...register("bank_name")}
                            className={inputClass}
                          />
                        </div>
                        <div>
                          <label className={labelClass}>Monthly household expenses</label>
                          <input
                            type="number"
                            step="0.01"
                            disabled={submitting}
                            {...register("monthly_household_expenses")}
                            className={inputClass}
                          />
                        </div>
                      </>
                    )}
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
      </div>
    </main>
  );
}
