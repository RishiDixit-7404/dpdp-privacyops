import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { formatDate } from "@/lib/format";
import type { ConsentSummaryResponse } from "@/lib/types";

export function ConsentSummaryCards({ summary }: { summary: ConsentSummaryResponse | null }) {
  const cards = [
    { label: "Total events", value: summary?.total_events ?? 0 },
    { label: "Granted events", value: summary?.granted_count ?? 0 },
    { label: "Withdrawn events", value: summary?.withdrawn_count ?? 0 },
    { label: "Purposes", value: summary?.purposes.length ?? 0 }
  ];

  return (
    <div className="grid gap-4 md:grid-cols-4">
      {cards.map((card) => (
        <Card key={card.label}>
          <CardHeader>
            <CardTitle className="text-sm text-muted-foreground">{card.label}</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-semibold text-foreground">{card.value}</div>
          </CardContent>
        </Card>
      ))}
      {summary && summary.purposes.length > 0 ? (
        <Card className="md:col-span-4">
          <CardHeader>
            <CardTitle>Purpose activity</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid gap-3 md:grid-cols-2">
              {summary.purposes.map((purpose) => (
                <div className="rounded-lg border border-border bg-white p-4" key={purpose.purpose}>
                  <div className="font-medium text-foreground">{purpose.purpose}</div>
                  <div className="mt-1 text-sm text-muted-foreground">
                    {purpose.granted_count} granted · {purpose.withdrawn_count} withdrawn
                  </div>
                  <div className="mt-1 text-xs text-muted-foreground">
                    Latest event: {purpose.latest_event_at ? formatDate(purpose.latest_event_at) : "None"}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      ) : null}
    </div>
  );
}
