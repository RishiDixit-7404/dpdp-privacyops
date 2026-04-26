import { RiskBadge } from "@/components/findings/risk-badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { formatEnumLabel } from "@/lib/format";
import type { RiskLevel, RiskSummary } from "@/lib/types";

const riskOrder: RiskLevel[] = ["critical", "high", "medium", "low"];

export function RiskSummarySection({ summary }: { summary: RiskSummary }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Risk Summary</CardTitle>
      </CardHeader>
      <CardContent className="grid gap-4">
        <div className="grid gap-3 md:grid-cols-4">
          {riskOrder.map((risk) => (
            <div className="rounded-lg border border-border bg-white p-4" key={risk}>
              <RiskBadge risk={risk} />
              <div className="mt-3 text-2xl font-semibold text-foreground">{summary.counts_by_risk_level[risk] ?? 0}</div>
            </div>
          ))}
        </div>
        <div className="text-sm text-muted-foreground">
          Highest risk level: {summary.highest_risk_level ? formatEnumLabel(summary.highest_risk_level) : "none"}
        </div>
      </CardContent>
    </Card>
  );
}
