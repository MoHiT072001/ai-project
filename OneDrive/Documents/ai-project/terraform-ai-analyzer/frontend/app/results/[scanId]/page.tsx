import { getResults } from "@/lib/api";
import { IssueList } from "@/components/IssueList";

export default async function ResultsPage({
  params
}: {
  params: Promise<{ scanId: string }>;
}) {
  const { scanId } = await params;
  const result = await getResults(scanId);

  const summary = result.summary ?? {};
  const hardIssues = summary.hard_issues ?? 0;
  const upgradesFound = summary.upgrades_found ?? 0;
  const confidencePct =
    summary.confidence !== undefined ? Math.round(summary.confidence * 100) : undefined;

  return (
    <div className="space-y-8">
      <div>
        <div className="text-xl font-semibold">Results</div>
        <div className="text-sm text-zinc-400">
          Scan ID: <span className="font-mono">{result.scan_id}</span>
        </div>
      </div>

      <section className="space-y-3">
        <div className="text-lg font-semibold">Analysis Summary</div>
        <div className="grid gap-4 md:grid-cols-3">
          <div className="rounded-lg border border-zinc-800 bg-zinc-950/60 p-4">
            <div className="text-xs uppercase tracking-wide text-zinc-500">Hard Issues</div>
            <div className="mt-1 text-2xl font-semibold">{hardIssues}</div>
          </div>
          <div className="rounded-lg border border-zinc-800 bg-zinc-950/60 p-4">
            <div className="text-xs uppercase tracking-wide text-zinc-500">
              Upgrades Found
            </div>
            <div className="mt-1 text-2xl font-semibold">{upgradesFound}</div>
          </div>
          <div className="rounded-lg border border-zinc-800 bg-zinc-950/60 p-4">
            <div className="text-xs uppercase tracking-wide text-zinc-500">
              Confidence
            </div>
            <div className="mt-1 text-2xl font-semibold">
              {confidencePct !== undefined ? `${confidencePct}%` : "—"}
            </div>
          </div>
        </div>
      </section>

      <section className="space-y-3">
        <div className="text-lg font-semibold">Changes / Upgrades Found</div>
        {result.changes?.length ? (
          <div className="space-y-3">
            {result.changes.map((c) => (
              <div
                key={c.id}
                className="rounded-lg border border-zinc-800 bg-zinc-950/60 p-4"
              >
                <div className="flex flex-wrap items-center gap-2">
                  <span className="text-sm font-semibold">{c.title}</span>
                </div>
                <div className="mt-1 text-xs uppercase tracking-wide text-zinc-500">
                  Change
                </div>
                <div className="mt-2 grid gap-4 md:grid-cols-2">
                  <div>
                    <div className="text-xs font-medium text-zinc-500">From</div>
                    <pre className="mt-1 whitespace-pre-wrap rounded-md bg-zinc-950 px-3 py-2 text-xs text-zinc-200">
                      {c.from}
                    </pre>
                  </div>
                  <div>
                    <div className="text-xs font-medium text-zinc-500">To</div>
                    <pre className="mt-1 whitespace-pre-wrap rounded-md bg-zinc-950 px-3 py-2 text-xs text-emerald-200">
                      {c.to}
                    </pre>
                  </div>
                </div>
                <div className="mt-2 text-sm text-zinc-300">{c.description}</div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-sm text-zinc-400">
            No concrete upgrades were proposed by the AI.
          </div>
        )}
      </section>

      <section className="space-y-3">
        <div className="text-lg font-semibold">Migration Guide</div>
        {result.migration_guide?.length ? (
          <ol className="space-y-3">
            {result.migration_guide
              .slice()
              .sort((a, b) => a.step - b.step)
              .map((step) => (
                <li
                  key={step.step}
                  className="rounded-lg border border-zinc-800 bg-zinc-950/60 p-4"
                >
                  <div className="text-sm font-semibold">
                    {step.step}. {step.title}
                  </div>
                  <div className="mt-1 text-sm text-zinc-300">{step.detail}</div>
                  {step.example_command ? (
                    <pre className="mt-2 whitespace-pre-wrap rounded-md bg-zinc-950 px-3 py-2 text-xs text-zinc-200">
                      {step.example_command}
                    </pre>
                  ) : null}
                </li>
              ))}
          </ol>
        ) : (
          <div className="text-sm text-zinc-400">
            No migration guide steps were generated.
          </div>
        )}
      </section>

      <section className="space-y-3">
        <div className="text-lg font-semibold">Recommendations for Your Code</div>
        {result.recommendations?.length ? (
          <div className="space-y-3">
            {result.recommendations.map((r) => (
              <div
                key={r.id}
                className="rounded-lg border border-zinc-800 bg-zinc-950/60 p-4"
              >
                <div className="text-sm font-semibold">{r.title}</div>
                <div className="mt-1 text-sm text-zinc-300">{r.description}</div>
                <div className="mt-2 text-sm">
                  <div className="text-zinc-500">Recommendation</div>
                  <div className="text-zinc-200">{r.recommendation}</div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-sm text-zinc-400">
            No high-level recommendations were generated beyond individual issues.
          </div>
        )}
      </section>

      <section className="space-y-3">
        <div className="text-lg font-semibold">Static Issues</div>
        <IssueList issues={result.static_issues ?? []} emptyText="No static issues detected." />
      </section>

      <section className="space-y-3">
        <div className="text-lg font-semibold">Policy Violations</div>
        <IssueList
          issues={result.policy_violations ?? []}
          emptyText="No policy violations detected."
        />
      </section>

      <section className="space-y-3">
        <div className="text-lg font-semibold">AI Architecture Insights</div>
        <IssueList
          issues={result.ai_architecture_insights ?? []}
          emptyText="No architecture insights returned."
        />
      </section>

      <section className="space-y-3">
        <div className="text-lg font-semibold">Attack Path Possibilities</div>
        <IssueList issues={result.ai_attack_paths ?? []} emptyText="No attack paths returned." />
      </section>

      <section className="space-y-3">
        <div className="text-lg font-semibold">Blast Radius Risks</div>
        <IssueList issues={result.ai_blast_radius ?? []} emptyText="No blast radius risks returned." />
      </section>

      <section className="space-y-3">
        <div className="text-lg font-semibold">Cost Optimization Suggestions</div>
        <IssueList
          issues={result.ai_cost_optimizations ?? []}
          emptyText="No cost optimization suggestions returned."
        />
      </section>

      {result.tooling_notes?.length ? (
        <section className="space-y-3">
          <div className="text-lg font-semibold">Tooling Notes</div>
          <IssueList issues={result.tooling_notes} emptyText="No tooling notes." />
        </section>
      ) : null}
    </div>
  );
}

