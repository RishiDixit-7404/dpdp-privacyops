import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { dataRequestStatusLabel, formatDate, formatEnumLabel } from "@/lib/format";
import type { DataRequestStatus, DsrSummary } from "@/lib/types";

const statusOrder: DataRequestStatus[] = ["new", "verifying", "in_progress", "completed", "rejected"];

export function DsrSummarySection({ summary }: { summary: DsrSummary }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>User Data Request Workflow</CardTitle>
      </CardHeader>
      <CardContent className="grid gap-4">
        <div className="grid gap-3 md:grid-cols-4">
          <div className="rounded-lg border border-border bg-white p-4">
            <div className="text-xs font-medium text-muted-foreground">Total requests</div>
            <div className="mt-2 text-2xl font-semibold text-foreground">{summary.total_requests}</div>
          </div>
          <div className="rounded-lg border border-border bg-white p-4">
            <div className="text-xs font-medium text-muted-foreground">Open requests</div>
            <div className="mt-2 text-2xl font-semibold text-foreground">{summary.open_requests}</div>
          </div>
          <div className="rounded-lg border border-border bg-white p-4">
            <div className="text-xs font-medium text-muted-foreground">Overdue requests</div>
            <div className="mt-2 text-2xl font-semibold text-foreground">{summary.overdue_requests}</div>
          </div>
          <div className="rounded-lg border border-border bg-white p-4">
            <div className="text-xs font-medium text-muted-foreground">Latest request</div>
            <div className="mt-2 text-sm text-foreground">
              {summary.latest_request_created_at ? formatDate(summary.latest_request_created_at) : "None"}
            </div>
          </div>
        </div>
        <div className="grid gap-3 md:grid-cols-2">
          <div className="grid gap-2">
            <div className="text-sm font-medium text-foreground">By status</div>
            <div className="flex flex-wrap gap-2">
              {statusOrder.map((status) => (
                <Badge className="bg-muted text-muted-foreground" key={status}>
                  {dataRequestStatusLabel(status)}: {summary.counts_by_status[status] ?? 0}
                </Badge>
              ))}
            </div>
          </div>
          <div className="grid gap-2">
            <div className="text-sm font-medium text-foreground">By request type</div>
            <div className="flex flex-wrap gap-2">
              {Object.entries(summary.counts_by_type).length > 0 ? (
                Object.entries(summary.counts_by_type).map(([type, count]) => (
                  <Badge className="bg-muted text-muted-foreground" key={type}>
                    {formatEnumLabel(type)}: {count}
                  </Badge>
                ))
              ) : (
                <span className="text-sm text-muted-foreground">No request types recorded.</span>
              )}
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
