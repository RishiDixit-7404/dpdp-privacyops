"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";

import { EvidenceReportView } from "@/components/reports/evidence-report-view";
import { apiErrorMessage, getEvidenceReport } from "@/lib/api";
import type { EvidenceReportResponse } from "@/lib/types";

export default function EvidenceReportPage({ params }: { params: { projectId: string } }) {
  const [report, setReport] = useState<EvidenceReportResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const loadReport = useCallback(async () => {
    setError(null);
    setIsLoading(true);
    try {
      setReport(await getEvidenceReport(params.projectId));
    } catch (requestError) {
      setError(apiErrorMessage(requestError));
    } finally {
      setIsLoading(false);
    }
  }, [params.projectId]);

  useEffect(() => {
    void loadReport();
  }, [loadReport]);

  return (
    <div className="grid gap-6">
      <div className="no-print">
        <Link className="text-sm font-medium text-primary" href={`/projects/${params.projectId}`}>
          Back to project
        </Link>
      </div>
      {isLoading ? <div className="text-sm text-muted-foreground">Loading evidence report...</div> : null}
      {error ? <div className="rounded-md bg-red-50 px-3 py-2 text-sm text-red-800">{error}</div> : null}
      {!isLoading && !error && !report ? (
        <div className="rounded-lg border border-dashed border-border bg-surface px-5 py-8 text-center text-sm text-muted-foreground">
          No report data is available yet.
        </div>
      ) : null}
      {report ? <EvidenceReportView report={report} /> : null}
    </div>
  );
}
