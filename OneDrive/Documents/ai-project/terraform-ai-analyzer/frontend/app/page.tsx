"use client";

import { useMemo, useState } from "react";
import { runScan } from "@/lib/api";

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
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const canScan = useMemo(() => code.trim().length > 0 && !loading, [code, loading]);

  async function onScan() {
    setError(null);
    setLoading(true);
    try {
      const { scan_id } = await runScan(code);
      window.location.href = `/results/${scan_id}`;
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-6">
      <div className="space-y-2">
        <div className="text-xl font-semibold">Paste Terraform code</div>
        <div className="text-sm text-zinc-400">
          Run a full scan combining static tools, OPA policy checks, dependency graph
          analysis, and AI reasoning.
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
            onClick={onScan}
            disabled={!canScan}
            className="rounded-lg bg-zinc-100 px-4 py-2 text-sm font-semibold text-zinc-950 disabled:opacity-50"
          >
            {loading ? "Scanning…" : "Run Scan"}
          </button>
          <button
            onClick={() => setCode(SAMPLE)}
            disabled={loading}
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
    </div>
  );
}

