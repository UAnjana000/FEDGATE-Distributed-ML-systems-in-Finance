import { FormEvent, useEffect, useMemo, useState } from "react";
import { fetchAlerts, fetchSnapshots, scoreBorrower } from "./api";
import { getCreditDecision } from "./decision";
import type { AlertItem, BorrowerInput, RiskScore, RiskSnapshot } from "./types";

const DEFAULT_FORM: BorrowerInput = {
  borrower_id: "",
  monthly_income: 50000,
  existing_emi: 8000,
  requested_loan_emi: 5000,
  debt_outstanding: 120000,
  account_balance_series: [],
  repayment_delay_series: [],
};

const ARCHITECTURE_FLOW = [
  "User Banking Input",
  "API Gateway",
  "Risk Engine",
  "Alerts Service",
  "FL Orchestrator",
  "Risk + Credit Decision",
];

function parseNumberSeries(input: string): number[] {
  return input
    .split(",")
    .map((item) => Number(item.trim()))
    .filter((value) => Number.isFinite(value));
}

export function App() {
  const [snapshots, setSnapshots] = useState<RiskSnapshot[]>([]);
  const [alerts, setAlerts] = useState<AlertItem[]>([]);
  const [loadingDashboard, setLoadingDashboard] = useState(true);
  const [dashboardError, setDashboardError] = useState<string | null>(null);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [scoreResult, setScoreResult] = useState<RiskScore | null>(null);
  const [formData, setFormData] = useState<BorrowerInput>(DEFAULT_FORM);
  const [balanceSeriesText, setBalanceSeriesText] = useState("");
  const [delaySeriesText, setDelaySeriesText] = useState("");

  const criticalCount = useMemo(
    () => snapshots.filter((item) => item.severity === "critical").length,
    [snapshots],
  );

  useEffect(() => {
    const load = async () => {
      try {
        const [riskData, alertData] = await Promise.all([fetchSnapshots(), fetchAlerts()]);
        setSnapshots(riskData);
        setAlerts(alertData);
        setDashboardError(null);
      } catch (err) {
        setDashboardError(err instanceof Error ? err.message : "Unknown error");
      } finally {
        setLoadingDashboard(false);
      }
    };
    void load();
    const timer = setInterval(() => void load(), 8000);
    return () => clearInterval(timer);
  }, []);

  const currentDecision = useMemo(
    () => (scoreResult ? getCreditDecision(scoreResult) : null),
    [scoreResult],
  );

  const onSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const payload: BorrowerInput = {
      ...formData,
      account_balance_series: parseNumberSeries(balanceSeriesText),
      repayment_delay_series: parseNumberSeries(delaySeriesText),
    };

    if (!payload.borrower_id.trim()) {
      setSubmitError("Borrower ID is required.");
      return;
    }

    if (
      payload.monthly_income <= 0 ||
      payload.existing_emi < 0 ||
      payload.requested_loan_emi < 0 ||
      payload.debt_outstanding < 0
    ) {
      setSubmitError("Please provide valid positive values for income and non-negative debts.");
      return;
    }

    setSubmitError(null);
    setSubmitting(true);
    try {
      const result = await scoreBorrower(payload);
      setScoreResult(result);
      setFormData((prev) => ({ ...prev, borrower_id: payload.borrower_id }));
    } catch (err) {
      setSubmitError(err instanceof Error ? err.message : "Failed to evaluate borrower");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="container">
      <header>
        <h1>Federated Financial Risk Dashboard</h1>
        <p>
          FEDGATE architecture-aligned visualization for borrower evaluation with rule-based risk and
          credit decisions.
        </p>
      </header>

      <section className="cards">
        <article className="card">
          <h2>Borrowers tracked</h2>
          <strong>{snapshots.length}</strong>
        </article>
        <article className="card">
          <h2>Critical alerts</h2>
          <strong>{criticalCount}</strong>
        </article>
        <article className="card">
          <h2>Total alerts</h2>
          <strong>{alerts.length}</strong>
        </article>
      </section>

      <section className="panel">
        <div className="panel-header">
          <h3>FEDGATE Architecture Flow</h3>
          <span>Live evaluation path</span>
        </div>
        <div className="architecture-flow">
          {ARCHITECTURE_FLOW.map((node, idx) => (
            <div className="flow-item" key={node}>
              <span className="flow-node">{node}</span>
              {idx < ARCHITECTURE_FLOW.length - 1 ? <span className="flow-arrow">→</span> : null}
            </div>
          ))}
        </div>
      </section>

      <section className="grid grid-three">
        <article className="panel">
          <div className="panel-header">
            <h3>Banking Details Input</h3>
            <span>Required for scoring</span>
          </div>
          <form className="form-grid" onSubmit={onSubmit}>
            <label>
              Borrower ID
              <input
                type="text"
                value={formData.borrower_id}
                onChange={(event) =>
                  setFormData((prev) => ({ ...prev, borrower_id: event.target.value }))
                }
                placeholder="ex: cust-1001"
                disabled={submitting}
              />
            </label>
            <label>
              Monthly Income
              <input
                type="number"
                min={1}
                value={formData.monthly_income}
                onChange={(event) =>
                  setFormData((prev) => ({
                    ...prev,
                    monthly_income: Number(event.target.value),
                  }))
                }
                disabled={submitting}
              />
            </label>
            <label>
              Existing EMI
              <input
                type="number"
                min={0}
                value={formData.existing_emi}
                onChange={(event) =>
                  setFormData((prev) => ({
                    ...prev,
                    existing_emi: Number(event.target.value),
                  }))
                }
                disabled={submitting}
              />
            </label>
            <label>
              Requested Loan EMI
              <input
                type="number"
                min={0}
                value={formData.requested_loan_emi}
                onChange={(event) =>
                  setFormData((prev) => ({
                    ...prev,
                    requested_loan_emi: Number(event.target.value),
                  }))
                }
                disabled={submitting}
              />
            </label>
            <label>
              Debt Outstanding
              <input
                type="number"
                min={0}
                value={formData.debt_outstanding}
                onChange={(event) =>
                  setFormData((prev) => ({
                    ...prev,
                    debt_outstanding: Number(event.target.value),
                  }))
                }
                disabled={submitting}
              />
            </label>
            <label>
              Account Balance Series (optional)
              <input
                type="text"
                value={balanceSeriesText}
                onChange={(event) => setBalanceSeriesText(event.target.value)}
                placeholder="ex: 100000, 98000, 96000"
                disabled={submitting}
              />
            </label>
            <label>
              Repayment Delay Series (optional)
              <input
                type="text"
                value={delaySeriesText}
                onChange={(event) => setDelaySeriesText(event.target.value)}
                placeholder="ex: 0, 1, 0, 2"
                disabled={submitting}
              />
            </label>
            <button type="submit" disabled={submitting}>
              {submitting ? "Evaluating..." : "Evaluate Borrower"}
            </button>
            {submitError && <p className="error">{submitError}</p>}
          </form>
        </article>

        <article className="panel">
          <div className="panel-header">
            <h3>Evaluation Result</h3>
            <span>Risk metrics + credit output</span>
          </div>
          {scoreResult ? (
            <div className="result-grid">
              <p>
                <strong>Borrower:</strong> {scoreResult.borrower_id}
              </p>
              <p>
                <strong>Risk Probability:</strong> {scoreResult.risk_probability.toFixed(2)}
              </p>
              <p>
                <strong>FOIR:</strong> {scoreResult.foir.toFixed(2)}
              </p>
              <p>
                <strong>Debt Burden:</strong> {scoreResult.debt_burden.toFixed(2)}
              </p>
              <p>
                <strong>Severity:</strong>{" "}
                <span className={`badge badge-${scoreResult.severity}`}>{scoreResult.severity}</span>
              </p>
              <p>
                <strong>Distress Flag:</strong> {scoreResult.distress_flag ? "Yes" : "No"}
              </p>
              <p>
                <strong>Decision:</strong>{" "}
                <span
                  className={`badge ${
                    currentDecision === "Reject"
                      ? "badge-critical"
                      : currentDecision === "Review"
                        ? "badge-high"
                        : "badge-low"
                  }`}
                >
                  {currentDecision}
                </span>
              </p>
            </div>
          ) : (
            <p>Submit borrower details to view calculated risk and credit decision.</p>
          )}
        </article>
      </section>

      {loadingDashboard && <p>Loading dashboard...</p>}
      {dashboardError && <p className="error">{dashboardError}</p>}

      <section className="grid">
        <article className="panel">
          <h3>Latest Risk Snapshots</h3>
          <table>
            <thead>
              <tr>
                <th>Borrower</th>
                <th>Risk</th>
                <th>FOIR</th>
                <th>Debt Burden</th>
                <th>Severity</th>
              </tr>
            </thead>
            <tbody>
              {snapshots.map((row) => (
                <tr key={`${row.borrower_id}-${row.created_at}`}>
                  <td>{row.borrower_id}</td>
                  <td>{row.risk_probability.toFixed(2)}</td>
                  <td>{row.foir.toFixed(2)}</td>
                  <td>{row.debt_burden.toFixed(2)}</td>
                  <td>
                    <span className={`badge badge-${row.severity}`}>{row.severity}</span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </article>
        <article className="panel">
          <h3>Alert Feed</h3>
          <ul>
            {alerts.map((item, idx) => (
              <li key={`${item.borrower_id}-${idx}`}>
                <span className={`badge badge-${item.severity}`}>{item.severity}</span>{" "}
                {item.message}
              </li>
            ))}
          </ul>
        </article>
      </section>
    </div>
  );
}
