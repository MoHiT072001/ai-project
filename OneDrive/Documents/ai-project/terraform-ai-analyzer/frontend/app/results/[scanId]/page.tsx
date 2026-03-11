import { getResults } from "@/lib/api";
import { IssueList } from "@/components/IssueList";

export default async function ResultsPage({
  params
}: {
  params: Promise<{ scanId: string }>;
}) {
  const { scanId } = await params;
  const result = await getResults(scanId);

  return (
    <div className="space-y-8">
      <div>
        <div className="text-xl font-semibold">Results</div>
        <div className="text-sm text-zinc-400">
          Scan ID: <span className="font-mono">{result.scan_id}</span>
        </div>
      </div>

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

