import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { EvidenceReportResponse } from "@/lib/types";

export function ReportSummaryCards({ report }: { report: EvidenceReportResponse }) {
  const cards = [
    { label: "Scans", value: report.scan_summary.scan_count },
    { label: "Findings", value: report.risk_summary.total_findings },
    { label: "Critical risks", value: report.risk_summary.critical_count },
    { label: "Open requests", value: report.dsr_summary.open_requests },
    { label: "Consent events", value: report.consent_summary.total_events }
  ];

  return (
    <div className="grid gap-4 md:grid-cols-5">
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
    </div>
  );
}
