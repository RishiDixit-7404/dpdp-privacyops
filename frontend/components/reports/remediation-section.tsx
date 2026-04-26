import { RiskBadge } from "@/components/findings/risk-badge";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { formatEnumLabel } from "@/lib/format";
import type { RemediationSummary } from "@/lib/types";

export function RemediationSection({ summary }: { summary: RemediationSummary }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Recommended Remediation</CardTitle>
      </CardHeader>
      <CardContent className="grid gap-4">
        <div className="grid gap-3 md:grid-cols-3">
          <div className="rounded-lg border border-border bg-white p-4">
            <div className="text-xs font-medium text-muted-foreground">Recommended actions</div>
            <div className="mt-2 text-2xl font-semibold text-foreground">{summary.total_recommended_actions}</div>
          </div>
          <div className="rounded-lg border border-border bg-white p-4">
            <div className="text-xs font-medium text-muted-foreground">Critical actions</div>
            <div className="mt-2 text-2xl font-semibold text-foreground">{summary.critical_actions}</div>
          </div>
          <div className="rounded-lg border border-border bg-white p-4">
            <div className="text-xs font-medium text-muted-foreground">High-priority actions</div>
            <div className="mt-2 text-2xl font-semibold text-foreground">{summary.high_priority_actions}</div>
          </div>
        </div>
        {summary.actions.length === 0 ? (
          <div className="rounded-lg border border-dashed border-border px-5 py-8 text-center text-sm text-muted-foreground">
            No remediation actions generated yet.
          </div>
        ) : (
          <div className="grid gap-3">
            {summary.actions.map((action) => (
              <div className="rounded-lg border border-border bg-white p-4" key={action.title}>
                <div className="flex flex-col gap-2 md:flex-row md:items-start md:justify-between">
                  <div>
                    <div className="font-semibold text-foreground">{action.title}</div>
                    <div className="mt-1 text-sm text-muted-foreground">{action.description}</div>
                  </div>
                  <RiskBadge risk={action.priority} />
                </div>
                <div className="mt-3 flex flex-wrap gap-2">
                  <Badge className="bg-muted text-muted-foreground">Fields: {action.affected_fields_count}</Badge>
                  {action.related_pii_types.map((type) => (
                    <Badge className="bg-muted text-muted-foreground" key={type}>
                      {formatEnumLabel(type)}
                    </Badge>
                  ))}
                  {action.related_sources.slice(0, 4).map((source) => (
                    <Badge className="bg-muted text-muted-foreground" key={source}>
                      {source}
                    </Badge>
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
