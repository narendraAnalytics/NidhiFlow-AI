import type {
  CustomerCreate,
  CustomerResponse,
  LoanApplicationCreate,
  LoanApplicationResponse,
  LoanApplicationSubmit,
  LoanDocumentCreate,
  LoanDocumentResponse,
} from "@/types/loan";
import type { DashboardStatsResponse } from "@/types/dashboard";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL;

async function post<TResponse>(
  path: string,
  body: unknown,
  idToken?: string,
): Promise<TResponse> {
  const res = await fetch(`${API_BASE_URL}${path}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...(idToken ? { Authorization: `Bearer ${idToken}` } : {}),
    },
    body: JSON.stringify(body),
  });

  if (!res.ok) {
    const detail = await res.text();
    throw new Error(detail || `Request to ${path} failed with status ${res.status}`);
  }

  return res.json() as Promise<TResponse>;
}

async function get<TResponse>(path: string, idToken?: string): Promise<TResponse> {
  const res = await fetch(`${API_BASE_URL}${path}`, {
    method: "GET",
    headers: {
      ...(idToken ? { Authorization: `Bearer ${idToken}` } : {}),
    },
  });

  if (!res.ok) {
    const detail = await res.text();
    throw new Error(detail || `Request to ${path} failed with status ${res.status}`);
  }

  return res.json() as Promise<TResponse>;
}

export function createCustomer(data: CustomerCreate, idToken?: string) {
  return post<CustomerResponse>("/customers", data, idToken);
}

export function createLoanApplication(data: LoanApplicationCreate, idToken?: string) {
  return post<LoanApplicationResponse>("/loan", data, idToken);
}

export function getDashboardStats(idToken?: string) {
  return get<DashboardStatsResponse>("/dashboard/stats", idToken);
}

export function createDocument(data: LoanDocumentCreate, idToken?: string) {
  return post<LoanDocumentResponse>("/documents", data, idToken);
}

export function submitLoanApplication(
  loanId: string,
  data: LoanApplicationSubmit,
  idToken?: string,
) {
  return post<LoanApplicationResponse>(`/loan/${loanId}/submit`, data, idToken);
}
