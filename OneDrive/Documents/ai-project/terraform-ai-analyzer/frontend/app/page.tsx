"use client";

import { useMemo, useState } from "react";
import { aiUpgrade, runScan, type UpgradeResult } from "@/lib/api";

const SAMPLE = `terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "us-east-1"
}

resource "aws_security_group" "web_sg" {
  name = "web-sg"

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_instance" "web" {
  ami           = "ami-12345678"
  instance_type = "t3.large"
  vpc_security_group_ids = [aws_security_group.web_sg.id]
}`;

export default function HomePage() {
  const [code, setCode] = useState<string>(SAMPLE);
  const [loadingScan, setLoadingScan] = useState(false);
  const [loadingUpgrade, setLoadingUpgrade] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [upgradeResult, setUpgradeResult] = useState<UpgradeResult | null>(null);

  const busy = loadingScan || loadingUpgrade;
  const canRun = useMemo(() => code.trim().length > 0 && !busy, [code, busy]);

  async function onScan() {
    setError(null);
    setLoadingScan(true);
    try {
      const { scan_id } = await runScan(code);
      window.location.href = `/results/${scan_id}`;
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setLoadingScan(false);
    }
  }

  async function onAiUpgrade() {
    setError(null);
    setUpgradeResult(null);
    setLoadingUpgrade(true);
    try {
      const res = await aiUpgrade(code);
      setUpgradeResult(res);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setLoadingUpgrade(false);
    }
  }

  return (
    <div className="space-y-6">
      <div className="space-y-2">
        <div className="text-xl font-semibold">Paste Terraform code</div>
        <div className="text-sm text-zinc-400">
          Use AI to generate an upgraded version of your Terraform, or run the full
          security scan.
        </div>
      </div>

      <div className="rounded-xl border border-zinc-800 bg-zinc-950/50 p-4">
        <textarea
          value={code}
          onChange={(e) => setCode(e.target.value)}
          spellCheck={false}
          className="h-[420px] w-full resize-y rounded-lg border border-zinc-800 bg-zinc-950 p-3 font-mono text-sm text-zinc-100 outline-none focus:ring-2 focus:ring-zinc-600"
        />
        <div className="mt-4 flex flex-wrap items-center gap-3">
          <button
            onClick={onAiUpgrade}
            disabled={!canRun}
            className="rounded-lg bg-zinc-100 px-4 py-2 text-sm font-semibold text-zinc-950 disabled:opacity-50"
          >
            {loadingUpgrade ? "Upgrading…" : "AI Upgrade Terraform"}
          </button>
          <button
            onClick={onScan}
            disabled={!canRun}
            className="rounded-lg border border-zinc-700 px-4 py-2 text-sm font-semibold text-zinc-200 disabled:opacity-50"
          >
            {loadingScan ? "Running scan…" : "Run Full Scan"}
          </button>
          <button
            onClick={() => setCode(SAMPLE)}
            disabled={busy}
            className="rounded-lg border border-zinc-700 px-4 py-2 text-sm font-semibold text-zinc-200 disabled:opacity-50"
          >
            Load sample
          </button>
          {error ? (
            <div className="text-sm text-rose-300">
              <span className="font-semibold">Error:</span> {error}
            </div>
          ) : null}
        </div>
      </div>

      {upgradeResult ? (
        <div className="space-y-4 rounded-xl border border-zinc-800 bg-zinc-950/60 p-4">
          <div className="text-lg font-semibold">AI Upgraded Terraform</div>
          <div className="grid gap-4 md:grid-cols-2">
            <div>
              <div className="text-xs font-medium uppercase tracking-wide text-zinc-500">
                Original
              </div>
              <pre className="mt-2 max-h-[420px] overflow-auto rounded-md bg-zinc-950 px-3 py-2 text-xs text-zinc-200">
                {code}
              </pre>
            </div>
            <div>
              <div className="text-xs font-medium uppercase tracking-wide text-zinc-500">
                Upgraded
              </div>
              <pre className="mt-2 max-h-[420px] overflow-auto rounded-md bg-zinc-950 px-3 py-2 text-xs text-emerald-200">
                {upgradeResult.upgraded_code}
              </pre>
            </div>
          </div>
          <div className="space-y-2">
            <div className="text-sm font-semibold">Suggestions</div>
            {upgradeResult.suggestions?.length ? (
              <ul className="space-y-2">
                {upgradeResult.suggestions.map((s, idx) => (
                  <li
                    key={`${s.title}-${idx}`}
                    className="rounded-lg border border-zinc-800 bg-zinc-950/80 p-3 text-sm"
                  >
                    <div className="font-semibold">{s.title}</div>
                    <div className="mt-1 text-zinc-300">{s.description}</div>
                    <div className="mt-1 text-zinc-200">
                      <span className="text-zinc-500">Recommendation: </span>
                      {s.recommendation}
                    </div>
                  </li>
                ))}
              </ul>
            ) : (
              <div className="text-sm text-zinc-400">
                No additional suggestions were returned by the AI.
              </div>
            )}
          </div>
        </div>
      ) : null}
    </div>
  );
}

