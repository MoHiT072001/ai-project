import clsx from "clsx";

export function SeverityBadge({
  severity
}: {
  severity: "low" | "medium" | "high" | "critical";
}) {
  const classes = clsx(
    "inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium",
    severity === "low" && "bg-emerald-950 text-emerald-200 ring-1 ring-emerald-800",
    severity === "medium" && "bg-amber-950 text-amber-200 ring-1 ring-amber-800",
    severity === "high" && "bg-orange-950 text-orange-200 ring-1 ring-orange-800",
    severity === "critical" && "bg-rose-950 text-rose-200 ring-1 ring-rose-800"
  );
  return <span className={classes}>{severity.toUpperCase()}</span>;
}

