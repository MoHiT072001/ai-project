export type Issue = {
  id: string;
  severity: "low" | "medium" | "high" | "critical";
  category:
    | "static"
    | "policy"
    | "architecture"
    | "attack_path"
    | "blast_radius"
    | "cost"
    | "tooling";
  resource: string;
  description: string;
  recommendation: string;
};

export type ScanResult = {
  scan_id: string;
  generated_at?: string;
  summary?: {
    hard_issues?: number;
    upgrades_found?: number;
    confidence?: number; // 0–1
  };
  changes?: {
    id: string;
    title: string;
    from: string;
    to: string;
    description: string;
    severity: Issue["severity"];
  }[];
  migration_guide?: {
    step: number;
    title: string;
    detail: string;
    example_command?: string;
  }[];
  recommendations?: {
    id: string;
    title: string;
    description: string;
    recommendation: string;
  }[];
  static_issues: Issue[];
  policy_violations: Issue[];
  ai_architecture_insights: Issue[];
  ai_attack_paths: Issue[];
  ai_blast_radius: Issue[];
  ai_cost_optimizations: Issue[];
  tooling_notes?: Issue[];
  graph?: unknown;
  inputs?: unknown;
};

const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000";

export async function runScan(terraform_code: string): Promise<{ scan_id: string }> {
  const r = await fetch(`${API_BASE}/scan`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ terraform_code })
  });
  if (!r.ok) {
    const text = await r.text();
    throw new Error(text || `Scan failed: ${r.status}`);
  }
  return await r.json();
}

export async function getResults(scanId: string): Promise<ScanResult> {
  const r = await fetch(`${API_BASE}/results/${scanId}`, { cache: "no-store" });
  if (!r.ok) {
    const text = await r.text();
    throw new Error(text || `Results fetch failed: ${r.status}`);
  }
  return await r.json();
}

