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
  age?: number;
  city?: string;
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
  credit_score?: number;
  existing_emi?: number;
  property_value?: number;
  down_payment?: number;
  employment_experience_years?: number;
  existing_loan_outstanding?: number;
  bank_name?: string;
  monthly_household_expenses?: number;
  business_name?: string;
  business_type?: string;
  industry?: string;
  business_vintage_years?: number;
  annual_turnover?: number;
  monthly_business_revenue?: number;
  monthly_net_profit?: number;
  gst_number?: string;
  udyam_registration_number?: string;
  cin_llpin?: string;
  number_of_employees?: number;
  existing_business_loan_outstanding?: number;
  business_bank_name?: string;
  collateral_required?: boolean;
  collateral_type?: string;
  collateral_value?: number;
  occupation_designation?: string;
  total_work_experience?: string;
  experience_current_employer?: string;
  property_type?: string;
  property_status?: string;
  builder_developer_name?: string;
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
