"use client";

import { useState } from "react";
import { Loader2, Plus, Send, FileCheck2 } from "lucide-react";
import { toast } from "sonner";
import { useAuth } from "@/contexts/auth-context";
import { createDocument, submitLoanApplication } from "@/lib/api";
import { uploadLoanDocument } from "@/lib/storage";
import type { DocumentType, LoanDocumentResponse } from "@/types/loan";
import { inputClass, labelClass } from "./page";

const DOCUMENT_TYPES: DocumentType[] = [
  "PAN Card",
  "Aadhaar",
  "Salary Slip",
  "Bank Statement",
  "ITR",
  "Property Papers",
  "Business Registration",
  "GST Certificate",
  "Passport",
  "Driving Licence",
  "Photo",
  "Signature",
  "Loan Application Form",
  "Income Proof",
  "Address Proof",
  "Other",
];

export function DocumentUploadSection({
  loanId,
  onSubmitted,
}: {
  loanId: string;
  onSubmitted: () => void;
}) {
  const { user } = useAuth();
  const [documentType, setDocumentType] = useState<DocumentType>("PAN Card");
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [documents, setDocuments] = useState<LoanDocumentResponse[]>([]);

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
    try {
      const idToken = await user.getIdToken();
      await submitLoanApplication(
        loanId,
        { changed_by: user.email ?? user.uid },
        idToken,
      );
      toast.success("Application submitted for processing.");
      onSubmitted();
    } catch {
      toast.error("Submission failed. Please try again.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="flex flex-col gap-5">
      <div>
        <h2 className="mb-3 text-[14px] font-bold text-[#0f1b33]">Upload documents</h2>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-[1fr_1fr_auto] sm:items-end">
          <div>
            <label className={labelClass}>Document type</label>
            <select
              value={documentType}
              onChange={(e) => setDocumentType(e.target.value as DocumentType)}
              disabled={uploading}
              className={inputClass}
            >
              {DOCUMENT_TYPES.map((type) => (
                <option key={type} value={type}>
                  {type}
                </option>
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

      <button
        type="button"
        onClick={onSubmitApplication}
        disabled={documents.length === 0 || submitting}
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
    </div>
  );
}
