import { ConsentSummarySection } from "@/components/reports/consent-summary-section";
import { DataInventorySection } from "@/components/reports/data-inventory-section";
import { DsrSummarySection } from "@/components/reports/dsr-summary-section";
import { PrintReportButton } from "@/components/reports/print-report-button";
import { ReadinessGapsSection } from "@/components/reports/readiness-gaps-section";
import { RemediationSection } from "@/components/reports/remediation-section";
import { ReportDisclaimer } from "@/components/reports/report-disclaimer";
import { ReportSummaryCards } from "@/components/reports/report-summary-cards";
import { RiskSummarySection } from "@/components/reports/risk-summary-section";
import { TopRisksSection } from "@/components/reports/top-risks-section";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { formatDate } from "@/lib/format";
import type { EvidenceReportResponse } from "@/lib/types";

export function EvidenceReportView({ report }: { report: EvidenceReportResponse }) {
  return (
    <article className="grid gap-6 print-report">
      <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-foreground">Evidence Report</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            DPDP readiness evidence for {report.project.name} · generated {formatDate(report.generated_at)} · v{report.report_version}
          </p>
        </div>
        <PrintReportButton />
      </div>

      <ReportDisclaimer text={report.disclaimer} />

      <Card>
        <CardHeader>
          <CardTitle>Executive Summary</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm leading-6 text-foreground">{report.executive_summary}</p>
        </CardContent>
      </Card>

      <ReportSummaryCards report={report} />
      <DataInventorySection inventory={report.data_inventory_summary} scanSummary={report.scan_summary} />
      <RiskSummarySection summary={report.risk_summary} />
      <TopRisksSection topRisks={report.top_risks} />
      <DsrSummarySection summary={report.dsr_summary} />
      <ConsentSummarySection summary={report.consent_summary} />
      <RemediationSection summary={report.remediation_summary} />
      <ReadinessGapsSection gaps={report.readiness_gaps} />
    </article>
  );
}
