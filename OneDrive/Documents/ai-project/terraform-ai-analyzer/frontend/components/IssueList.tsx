import { Issue } from "@/lib/api";
import { SeverityBadge } from "@/components/SeverityBadge";

export function IssueList({
  issues,
  emptyText
}: {
  issues: Issue[];
  emptyText: string;
}) {
  if (!issues?.length) {
    return <div className="text-sm text-zinc-400">{emptyText}</div>;
  }

  return (
    <div className="space-y-3">
      {issues.map((i) => (
        <div
          key={i.id}
          className="rounded-lg border border-zinc-800 bg-zinc-950/50 p-4"
        >
          <div className="flex flex-wrap items-center gap-2">
            <SeverityBadge severity={i.severity} />
            <div className="text-sm font-semibold">{i.description}</div>
          </div>
          <div className="mt-2 text-sm text-zinc-300">
            <span className="text-zinc-500">Resource:</span> {i.resource}
          </div>
          <div className="mt-2 text-sm">
            <div className="text-zinc-500">Recommendation</div>
            <div className="text-zinc-200">{i.recommendation}</div>
          </div>
        </div>
      ))}
    </div>
  );
}

