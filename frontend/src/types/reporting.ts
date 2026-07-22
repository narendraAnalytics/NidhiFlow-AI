import type { LoanStatus, LoanType } from "@/types/loan";

export type TimelineEventCategory = "status_change" | "workflow_event" | "node_execution";

export interface LoanTimelineEvent {
  timestamp: string;
  category: TimelineEventCategory;
  title: string;
  description: string | null;
  metadata: Record<string, unknown>;
}

export interface LoanSummary {
  loan_type: LoanType;
  requested_amount: number;
  status: LoanStatus;
  created_at: string;
}

export interface CustomerSummary {
  full_name: string;
}

export interface ValidationSummary {
  validation_status: string;
  confidence: number;
  missing_documents: string[];
  field_mismatches: string[];
}

export interface LoanTimelineResponse {
  loan_application_id: string;
  loan: LoanSummary;
  customer: CustomerSummary;
  validation_summary: ValidationSummary | null;
  events: LoanTimelineEvent[];
}
