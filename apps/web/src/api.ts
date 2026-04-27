import type { AlertItem, RiskSnapshot } from "./types";

const API_BASE = "http://localhost:8000";

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
