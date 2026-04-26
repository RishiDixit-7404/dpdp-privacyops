import { RiskBadge } from "@/components/findings/risk-badge";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { formatEnumLabel } from "@/lib/format";
import type { ReadinessGap } from "@/lib/types";

export function ReadinessGapsSection({ gaps }: { gaps: ReadinessGap[] }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Readiness Gaps</CardTitle>
      </CardHeader>
      <CardContent>
        {gaps.length === 0 ? (
          <div className="rounded-lg border border-dashed border-border px-5 py-8 text-center text-sm text-muted-foreground">
            No readiness gaps generated from the current project data.
          </div>
        ) : (
          <div className="grid gap-3">
            {gaps.map((gap) => (
              <div className="rounded-lg border border-border bg-white p-4" key={`${gap.area}-${gap.message}`}>
                <div className="flex flex-col gap-2 md:flex-row md:items-start md:justify-between">
                  <div className="grid gap-2">
                    <div className="flex flex-wrap items-center gap-2">
                      <RiskBadge risk={gap.severity} />
                      <Badge className="bg-muted text-muted-foreground">{formatEnumLabel(gap.area)}</Badge>
                    </div>
                    <div className="font-medium text-foreground">{gap.message}</div>
                    <div className="text-sm text-muted-foreground">{gap.suggested_next_step}</div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
