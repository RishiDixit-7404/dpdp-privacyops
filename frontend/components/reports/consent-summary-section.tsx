import { ConsentStatusBadge } from "@/components/consent/consent-status-badge";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { formatDate } from "@/lib/format";
import type { ConsentReportSummary } from "@/lib/types";

export function ConsentSummarySection({ summary }: { summary: ConsentReportSummary }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Consent Event Ledger</CardTitle>
      </CardHeader>
      <CardContent className="grid gap-4">
        <div className="grid gap-3 md:grid-cols-4">
          <div className="rounded-lg border border-border bg-white p-4">
            <div className="text-xs font-medium text-muted-foreground">Total events</div>
            <div className="mt-2 text-2xl font-semibold text-foreground">{summary.total_events}</div>
          </div>
          <div className="rounded-lg border border-border bg-white p-4">
            <ConsentStatusBadge status="granted" />
            <div className="mt-2 text-2xl font-semibold text-foreground">{summary.granted_count}</div>
          </div>
          <div className="rounded-lg border border-border bg-white p-4">
            <ConsentStatusBadge status="withdrawn" />
            <div className="mt-2 text-2xl font-semibold text-foreground">{summary.withdrawn_count}</div>
          </div>
          <div className="rounded-lg border border-border bg-white p-4">
            <div className="text-xs font-medium text-muted-foreground">Latest event</div>
            <div className="mt-2 text-sm text-foreground">
              {summary.latest_event_at ? formatDate(summary.latest_event_at) : "None"}
            </div>
          </div>
        </div>
        <div className="grid gap-2">
          <div className="text-sm font-medium text-foreground">Purposes</div>
          {summary.purposes.length === 0 ? (
            <div className="text-sm text-muted-foreground">No consent purposes recorded.</div>
          ) : (
            <div className="grid gap-3 md:grid-cols-2">
              {summary.purposes.map((purpose) => (
                <div className="rounded-lg border border-border bg-white p-4" key={purpose.purpose}>
                  <div className="font-medium text-foreground">{purpose.purpose}</div>
                  <div className="mt-2 flex flex-wrap gap-2">
                    <Badge className="bg-muted text-muted-foreground">Granted: {purpose.granted_count}</Badge>
                    <Badge className="bg-muted text-muted-foreground">Withdrawn: {purpose.withdrawn_count}</Badge>
                  </div>
                  <div className="mt-2 text-xs text-muted-foreground">
                    Latest event: {purpose.latest_event_at ? formatDate(purpose.latest_event_at) : "None"}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
