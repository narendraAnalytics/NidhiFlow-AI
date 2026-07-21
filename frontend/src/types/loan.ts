export type LoanType = "Home" | "Personal" | "Business";

export type LoanStatus =
  | "Draft"
  | "Documents Uploaded"
  | "Processing"
  | "Human Review"
  | "Approved"
  | "Rejected"
  | "Completed";

export type DocumentType =
  | "PAN Card"
  | "Aadhaar"
  | "Salary Slip"
  | "Bank Statement"
  | "ITR"
  | "Property Papers"
  | "Business Registration"
  | "GST Certificate"
  | "Passport"
  | "Driving Licence"
  | "Photo"
  | "Signature"
  | "Loan Application Form"
  | "Income Proof"
  | "Address Proof"
  | "Other";

export type DocumentStatus = "Uploaded" | "Verified" | "Rejected";

export interface CustomerCreate {
  full_name: string;
  email: string;
  phone: string;
  pan: string;
  aadhaar: string;
  address?: string;
}

export interface CustomerResponse extends CustomerCreate {
  id: string;
  created_at: string;
  updated_at: string;
}

export interface LoanApplicationCreate {
  customer_id: string;
  loan_type: LoanType;
  requested_amount: number;
  loan_purpose?: string;
  employment_type?: string;
  monthly_income?: number;
  employer?: string;
  tenure?: number;
  interest_rate?: number;
  branch?: string;
}

export interface LoanApplicationResponse extends LoanApplicationCreate {
  id: string;
  status: LoanStatus;
  created_at: string;
  updated_at: string;
}

export interface LoanApplicationSubmit {
  changed_by?: string;
  notes?: string;
}

export interface LoanDocumentCreate {
  loan_application_id: string;
  document_name: string;
  document_type: DocumentType;
  firebase_url?: string;
  uploaded_by?: string;
}

export interface LoanDocumentResponse extends LoanDocumentCreate {
  id: string;
  upload_time: string;
  status: DocumentStatus;
}
