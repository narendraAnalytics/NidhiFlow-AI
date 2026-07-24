"use client";

import { useState } from "react";
import { Loader2, Plus, Send, FileCheck2 } from "lucide-react";
import { toast } from "sonner";
import { useAuth } from "@/contexts/auth-context";
import { createDocument, submitLoanApplication } from "@/lib/api";
import { uploadLoanDocument } from "@/lib/storage";
import type { DocumentCategory, DocumentType, LoanDocumentResponse, LoanType } from "@/types/loan";
import { SubmitProgressStepper, type SubmitOutcome } from "@/components/loan/submit-progress-stepper";
import { inputClass, labelClass } from "./page";

const DOCUMENT_CHECKLIST_BY_LOAN_TYPE: Record<
  LoanType,
  { category: DocumentCategory; type: DocumentType }[]
> = {
  Home: [
    { category: "Identity Proof", type: "PAN Card" },
    { category: "Identity Proof", type: "Aadhaar" },
    { category: "Income Proof", type: "Form 16" },
    { category: "Income Proof", type: "Salary Slip" },
    { category: "Income Proof", type: "Bank Statement" },
    { category: "Property Documents", type: "Sale Agreement" },
    { category: "Property Documents", type: "Property Valuation Report" },
    { category: "Property Documents", type: "Property Tax Receipt" },
    { category: "Property Documents", type: "Encumbrance Certificate" },
    { category: "Property Documents", type: "Occupancy Certificate" },
    { category: "Property Documents", type: "Sale Deed" },
  ],
  Personal: [
    { category: "Identity Proof", type: "PAN Card" },
    { category: "Identity Proof", type: "Aadhaar" },
    { category: "Income Proof", type: "Form 16" },
    { category: "Income Proof", type: "Salary Slip" },
    { category: "Income Proof", type: "Bank Statement" },
    { category: "Income Proof", type: "ITR" },
    { category: "Identity Proof", type: "Employee ID" },
  ],
  Business: [
    { category: "Identity Proof", type: "PAN Card" },
    { category: "Identity Proof", type: "Aadhaar" },
    { category: "Business Documents", type: "GST Certificate" },
    { category: "Business Documents", type: "Udyam Certificate" },
    { category: "Business Documents", type: "Shop License" },
    { category: "Business Documents", type: "Partnership Deed" },
    { category: "Business Documents", type: "MOA" },
    { category: "Business Documents", type: "AOA" },
    { category: "Business Documents", type: "CIN Certificate" },
    { category: "Income Proof", type: "Bank Statement" },
    { category: "Income Proof", type: "ITR" },
    { category: "Business Documents", type: "Balance Sheet" },
    { category: "Business Documents", type: "Profit & Loss Statement" },
    { category: "Business Documents", type: "GST Returns" },
    { category: "Business Documents", type: "Audit Report" },
  ],
};

export function DocumentUploadSection({
  loanId,
  loanType,
  onSubmitted,
  initialDocuments = [],
}: {
  loanId: string;
  loanType: LoanType;
  onSubmitted: () => void;
  initialDocuments?: LoanDocumentResponse[];
}) {
  const { user } = useAuth();
  const checklist = DOCUMENT_CHECKLIST_BY_LOAN_TYPE[loanType];
  const [documentType, setDocumentType] = useState<DocumentType>(checklist[0].type);
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [submitOutcome, setSubmitOutcome] = useState<SubmitOutcome>(null);
  const [documents, setDocuments] = useState<LoanDocumentResponse[]>(initialDocuments);

  const categories = Array.from(new Set(checklist.map((c) => c.category)));

  const onAddDocument = async () => {
    if (!file || !user) return;
    setUploading(true);
    try {
      const idToken = await user.getIdToken();
      const downloadUrl = await uploadLoanDocument(loanId, documentType, file);
      const document = await createDocument(
        {
          loan_application_id: loanId,
          document_name: file.name,
          document_type: documentType,
          firebase_url: downloadUrl,
          uploaded_by: user.email ?? user.uid,
        },
        idToken,
      );
      setDocuments((prev) => [...prev, document]);
      setFile(null);
      toast.success(`${documentType} uploaded.`);
    } catch {
      toast.error("Upload failed. Please try again.");
    } finally {
      setUploading(false);
    }
  };

  const onSubmitApplication = async () => {
    if (!user) return;
    setSubmitting(true);
    setSubmitOutcome(null);
    try {
      const idToken = await user.getIdToken();
      const result = await submitLoanApplication(
        loanId,
        { changed_by: user.email ?? user.uid },
        idToken,
      );
      const outcome: SubmitOutcome = result.status === "Human Review" ? "human_review" : "processing";
      setSubmitOutcome(outcome);
      toast.success(
        outcome === "human_review"
          ? "Application flagged for human review."
          : "Application submitted for processing.",
      );
      setTimeout(onSubmitted, 1500);
    } catch {
      setSubmitOutcome("failed");
      toast.error("Submission failed. Please try again.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="flex flex-col gap-5">
      <div>
        <div className="mb-3 flex items-center justify-between">
          <h2 className="text-[14px] font-bold text-[#0f1b33]">Upload documents</h2>
          <span className="text-[12.5px] font-semibold text-[#5b6b8c]">
            {documents.length} file{documents.length === 1 ? "" : "s"} uploaded
          </span>
        </div>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-[1fr_1fr_auto] sm:items-end">
          <div>
            <label className={labelClass}>Document type</label>
            <select
              value={documentType}
              onChange={(e) => setDocumentType(e.target.value as DocumentType)}
              disabled={uploading}
              className={inputClass}
            >
              {categories.map((category) => (
                <optgroup key={category} label={category}>
                  {checklist
                    .filter((c) => c.category === category)
                    .map(({ type }) => (
                      <option key={type} value={type}>
                        {type}
                      </option>
                    ))}
                </optgroup>
              ))}
            </select>
          </div>
          <div>
            <label className={labelClass}>File</label>
            <input
              type="file"
              onChange={(e) => setFile(e.target.files?.[0] ?? null)}
              disabled={uploading}
              className="w-full rounded-xl border border-[#e2e8f5] bg-white p-3 text-[13.5px] text-[#5b6b8c] file:mr-3 file:rounded-lg file:border-0 file:bg-[#EEF2FF] file:px-3 file:py-1.5 file:text-[#3B82F6] file:font-semibold"
            />
          </div>
          <button
            type="button"
            onClick={onAddDocument}
            disabled={!file || uploading}
            className="inline-flex items-center justify-center gap-2 rounded-xl border border-[#e2e8f5] bg-white px-5 py-3 text-[14px] font-bold text-[#0f1b33] transition-colors hover:bg-[#f8fbff] disabled:cursor-not-allowed disabled:opacity-50"
          >
            {uploading ? <Loader2 size={17} className="animate-spin" /> : <Plus size={17} />}
            Add
          </button>
        </div>
      </div>

      {documents.length > 0 && (
        <div className="flex flex-col gap-2 rounded-2xl border border-[#e2e8f5] bg-[#f8fbff] p-4">
          {documents.map((doc) => (
            <div key={doc.id} className="flex items-center gap-2.5 text-[13.5px] text-[#0f1b33]">
              <FileCheck2 size={15} className="shrink-0 text-[#22C55E]" />
              <span className="truncate">{doc.document_name}</span>
              <span className="ml-auto shrink-0 text-[#9aa8c2]">{doc.document_type}</span>
            </div>
          ))}
        </div>
      )}

      {(submitting || submitOutcome !== null) && <SubmitProgressStepper outcome={submitOutcome} />}

      {submitOutcome !== "failed" ? (
        <button
          type="button"
          onClick={onSubmitApplication}
          disabled={documents.length === 0 || submitting || submitOutcome !== null}
          className="nf-cta mt-2 inline-flex items-center justify-center gap-2 rounded-2xl bg-gradient-to-r from-[#26D9FF] via-[#3B82F6] to-[#A855F7] py-3.5 text-[15px] font-extrabold text-white shadow-[0_10px_30px_rgba(59,130,246,0.4)] transition-all disabled:cursor-not-allowed disabled:opacity-70"
        >
          Submit application
          <Send size={17} />
        </button>
      ) : (
        <button
          type="button"
          onClick={() => setSubmitOutcome(null)}
          className="nf-cta mt-2 inline-flex items-center justify-center gap-2 rounded-2xl bg-gradient-to-r from-[#26D9FF] via-[#3B82F6] to-[#A855F7] py-3.5 text-[15px] font-extrabold text-white shadow-[0_10px_30px_rgba(59,130,246,0.4)] transition-all"
        >
          Try again
          <Send size={17} />
        </button>
      )}
    </div>
  );
}
