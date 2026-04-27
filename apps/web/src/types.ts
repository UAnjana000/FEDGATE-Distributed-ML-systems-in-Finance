export type RiskSnapshot = {
  borrower_id: string;
  risk_probability: number;
  foir: number;
  debt_burden: number;
  severity: string;
  created_at: string;
};

export type AlertItem = {
  borrower_id: string;
  severity: string;
  message: string;
  created_at: string;
};
