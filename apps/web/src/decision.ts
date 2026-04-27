import type { RiskScore } from "./types";

export type CreditDecision = "Approve" | "Review" | "Reject";

export function getCreditDecision(score: RiskScore): CreditDecision {
  if (score.severity === "critical" || score.risk_probability >= 0.75 || score.foir >= 0.65) {
    return "Reject";
  }

  if (score.severity === "high" || score.distress_flag || score.risk_probability >= 0.6) {
    return "Review";
  }

  return "Approve";
}
