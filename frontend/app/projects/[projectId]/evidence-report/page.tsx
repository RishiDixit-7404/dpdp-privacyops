"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";

import { RiskBadge } from "@/components/findings/risk-badge";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { apiErrorMessage, getEvidenceReport } from "@/lib/api";
import { formatConfidence, formatDate, formatEnumLabel, sourceTypeLabel } from "@/lib/format";
import type { EvidenceReport } from "@/lib/types";

export default function EvidenceReportPage({ params }: { params: { projectId: string } }) {
  const [report, setReport] = useState<EvidenceReport | null>(null);
  const [error, setError] = useState<string | null>(null);

  const loadReport = useCallback(async () => {
    setError(null);
    try {
      setReport(await getEvidenceReport(params.projectId));
    } catch (requestError) {
      setError(apiErrorMessage(requestError));
    }
  }, [params.projectId]);

  useEffect(() => {
    void loadReport();
  }, [loadReport]);

  return (
    <div className="grid gap-6">
      <div>
        <Link className="text-sm font-medium text-primary" href={`/projects/${params.projectId}`}>
          Back to project
        </Link>
        <h1 className="mt-2 text-2xl font-semibold text-foreground">Evidence Report</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          {report
            ? `${report.project.organization_name} · ${report.project.name} · generated ${formatDate(report.generated_at)}`
            : "Loading evidence report..."}
        </p>
      </div>

      {error ? <div className="rounded-md bg-red-50 px-3 py-2 text-sm text-red-800">{error}</div> : null}
      {!report && !error ? <div className="text-sm text-muted-foreground">Loading report...</div> : null}

      {report ? (
        <>
          <Card>
            <CardHeader>
              <CardTitle>Scope</CardTitle>
            </CardHeader>
            <CardContent className="grid gap-3 text-sm text-muted-foreground">
              <p>{report.trust_positioning}</p>
              <p>{report.evidence_scope}</p>
              <p>{report.technical_evidence_language}</p>
              <div className="rounded-md bg-amber-50 px-3 py-2 text-amber-900">
                {report.legal_certification_disclaimer}
              </div>
            </CardContent>
          </Card>

          <section className="grid gap-4 md:grid-cols-2">
            <ReadinessCard title="DSR readiness" readiness={report.dsr_readiness} />
            <ReadinessCard title="Consent readiness" readiness={report.consent_readiness} />
          </section>

          <section className="grid gap-4 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>Systems scanned</CardTitle>
              </CardHeader>
              <CardContent className="grid gap-3">
                {report.systems_scanned.map((system) => (
                  <div className="rounded-md border border-border p-3 text-sm" key={`${system.source_type}-${system.name}`}>
                    <div className="flex flex-wrap items-center gap-2">
                      <span className="font-medium text-foreground">{system.name}</span>
                      <Badge>{sourceTypeLabel(system.source_type)}</Badge>
                    </div>
                    <div className="mt-2 text-muted-foreground">
                      {system.finding_count} findings · {system.high_or_critical_count} high or critical
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Data categories</CardTitle>
              </CardHeader>
              <CardContent className="grid gap-3">
                {report.data_categories.map((category) => (
                  <div className="flex flex-wrap items-center justify-between gap-2 text-sm" key={category.pii_type}>
                    <span className="font-medium text-foreground">{formatEnumLabel(category.pii_type)}</span>
                    <div className="flex items-center gap-2">
                      <span className="text-muted-foreground">{category.finding_count}</span>
                      <RiskBadge risk={category.highest_risk_level} />
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>
          </section>

          <Card>
            <CardHeader>
              <CardTitle>Top risks</CardTitle>
            </CardHeader>
            <CardContent className="grid gap-3">
              {report.top_risks.map((risk) => (
                <div className="rounded-md border border-border p-3 text-sm" key={`${risk.table_or_file}-${risk.field_name}`}>
                  <div className="flex flex-wrap items-center gap-2">
                    <RiskBadge risk={risk.risk_level} />
                    <span className="font-medium text-foreground">
                      {risk.table_or_file}.{risk.field_name}
                    </span>
                    <span className="text-muted-foreground">{formatConfidence(risk.confidence_score)}</span>
                  </div>
                  <div className="mt-2 text-muted-foreground">
                    {formatEnumLabel(risk.pii_type)} · {risk.source_name}
                  </div>
                  {risk.masked_examples.length ? (
                    <div className="mt-2 flex flex-wrap gap-2">
                      {risk.masked_examples.map((example) => (
                        <Badge className="bg-muted" key={example}>
                          {example}
                        </Badge>
                      ))}
                    </div>
                  ) : null}
                  <p className="mt-2 text-muted-foreground">{risk.suggested_action}</p>
                </div>
              ))}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Remediation gaps</CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="grid gap-2 text-sm text-muted-foreground">
                {report.remediation_gaps.map((gap) => (
                  <li key={gap}>{gap}</li>
                ))}
              </ul>
            </CardContent>
          </Card>
        </>
      ) : null}
    </div>
  );
}

function ReadinessCard({
  readiness,
  title
}: {
  readiness: EvidenceReport["dsr_readiness"];
  title: string;
}) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>{title}</CardTitle>
      </CardHeader>
      <CardContent className="grid gap-3 text-sm">
        <div>
          <Badge>{formatEnumLabel(readiness.status)}</Badge>
        </div>
        <p className="text-muted-foreground">{readiness.summary}</p>
        <dl className="grid gap-2 sm:grid-cols-2">
          {Object.entries(readiness.metrics).map(([key, value]) => (
            <div key={key}>
              <dt className="text-xs font-medium text-muted-foreground">{formatEnumLabel(key)}</dt>
              <dd className="text-lg font-semibold text-foreground">{value}</dd>
            </div>
          ))}
        </dl>
      </CardContent>
    </Card>
  );
}
