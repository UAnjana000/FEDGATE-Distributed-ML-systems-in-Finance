export type Severity = "low" | "medium" | "high" | "critical";

export type RiskSnapshot = {
  borrower_id: string;
  risk_probability: number;
  foir: number;
  debt_burden: number;
  severity: Severity;
  created_at: string;
};

export type AlertItem = {
  borrower_id: string;
  severity: Severity;
  message: string;
  created_at: string;
};

export type BorrowerInput = {
  borrower_id: string;
  monthly_income: number;
  existing_emi: number;
  requested_loan_emi: number;
  debt_outstanding: number;
  account_balance_series: number[];
  repayment_delay_series: number[];
};

export type RiskScore = {
  borrower_id: string;
  risk_probability: number;
  foir: number;
  debt_burden: number;
  distress_flag: boolean;
  severity: Severity;
  generated_at: string;
};
