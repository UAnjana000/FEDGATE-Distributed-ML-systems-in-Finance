import { useEffect, useMemo, useState } from "react";
import { fetchAlerts, fetchSnapshots } from "./api";
import type { AlertItem, RiskSnapshot } from "./types";

export function App() {
  const [snapshots, setSnapshots] = useState<RiskSnapshot[]>([]);
  const [alerts, setAlerts] = useState<AlertItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

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
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Unknown error");
      } finally {
        setLoading(false);
      }
    };
    void load();
    const timer = setInterval(() => void load(), 8000);
    return () => clearInterval(timer);
  }, []);

  return (
    <div className="container">
      <header>
        <h1>Federated Financial Risk Dashboard</h1>
        <p>Monitoring FOIR, debt burden, distress and alerts without raw data centralization.</p>
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

      {loading && <p>Loading dashboard...</p>}
      {error && <p className="error">{error}</p>}

      <section className="grid">
        <article>
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
                  <td>{row.severity}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </article>
        <article>
          <h3>Alert Feed</h3>
          <ul>
            {alerts.map((item, idx) => (
              <li key={`${item.borrower_id}-${idx}`}>
                <span>[{item.severity}] </span>
                {item.message}
              </li>
            ))}
          </ul>
        </article>
      </section>
    </div>
  );
}
