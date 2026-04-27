import type { AlertItem, BorrowerInput, RiskScore, RiskSnapshot } from "./types";

const API_BASE = import.meta.env.VITE_API_BASE ?? "http://localhost:8000";

export async function fetchSnapshots(): Promise<RiskSnapshot[]> {
  const res = await fetch(`${API_BASE}/borrowers/snapshots`);
  if (!res.ok) throw new Error("Failed to fetch snapshots");
  const data = (await res.json()) as { items: RiskSnapshot[] };
  return data.items;
}

export async function fetchAlerts(): Promise<AlertItem[]> {
  const res = await fetch(`${API_BASE}/alerts`);
  if (!res.ok) throw new Error("Failed to fetch alerts");
  const data = (await res.json()) as { items: AlertItem[] };
  return data.items;
}

export async function scoreBorrower(payload: BorrowerInput): Promise<RiskScore> {
  const res = await fetch(`${API_BASE}/borrowers/score`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    throw new Error("Failed to evaluate borrower");
  }

  return (await res.json()) as RiskScore;
}
