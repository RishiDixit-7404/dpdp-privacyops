import { Card, CardContent } from "@/components/ui/card";
import type { ScanSummary } from "@/lib/types";

export function ScanSummaryCards({ summary }: { summary: ScanSummary | null }) {
  const values = summary
    ? [
        { label: "Total findings", value: summary.total_findings },
        { label: "Critical", value: summary.counts_by_risk_level.critical },
        { label: "High", value: summary.counts_by_risk_level.high },
        { label: "Medium", value: summary.counts_by_risk_level.medium },
        { label: "Low", value: summary.counts_by_risk_level.low }
      ]
    : [
        { label: "Total findings", value: "—" },
        { label: "Critical", value: "—" },
        { label: "High", value: "—" },
        { label: "Medium", value: "—" },
        { label: "Low", value: "—" }
      ];

  return (
    <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-5">
      {values.map((item) => (
        <Card key={item.label}>
          <CardContent className="py-4">
            <div className="text-xs font-medium uppercase tracking-normal text-muted-foreground">{item.label}</div>
            <div className="mt-2 text-2xl font-semibold text-foreground">{item.value}</div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}

