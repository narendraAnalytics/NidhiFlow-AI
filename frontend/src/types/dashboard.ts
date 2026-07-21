import type { LoanStatus, LoanType } from "@/types/loan";

export interface PipelineStageCount {
  stage: string;
  count: number;
}

export interface StatusDistributionSlice {
  status: string;
  count: number;
  percentage: number;
}

export interface TrendPoint {
  date: string;
  applications: number;
  approved: number;
}

export interface RecentApplicationItem {
  id: string;
  loan_type: LoanType;
  customer_name: string;
  status: LoanStatus;
  requested_amount: number;
  created_at: string;
}

export interface DashboardStatsResponse {
  total_applications: number;
  in_process: number;
  approved: number;
  avg_processing_days: number | null;
  success_rate: number;
  total_disbursed_amount: number;
  pipeline: PipelineStageCount[];
  conversion_rate: number;
  status_distribution: StatusDistributionSlice[];
  trend: TrendPoint[];
  recent: RecentApplicationItem[];
}
