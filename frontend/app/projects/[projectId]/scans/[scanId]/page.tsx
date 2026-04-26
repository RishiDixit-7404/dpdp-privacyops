"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";

import { FindingsTable } from "@/components/findings/findings-table";
import { ScanSummaryCards } from "@/components/scans/scan-summary-cards";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { apiErrorMessage, getScan, getScanFindings } from "@/lib/api";
import { formatDate } from "@/lib/format";
import type { FindingListResponse, ScanDetail } from "@/lib/types";

export default function ScanDetailPage({ params }: { params: { projectId: string; scanId: string } }) {
  const [scan, setScan] = useState<ScanDetail | null>(null);
  const [findings, setFindings] = useState<FindingListResponse | null>(null);
  const [offset, setOffset] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const limit = 100;

  const loadData = useCallback(async (nextOffset: number) => {
    setError(null);
    try {
      const [scanResponse, findingsResponse] = await Promise.all([
        getScan(params.scanId),
        getScanFindings(params.scanId, { limit, offset: nextOffset })
      ]);
      setScan(scanResponse);
      setFindings(findingsResponse);
    } catch (requestError) {
      setError(apiErrorMessage(requestError));
    }
  }, [params.scanId]);

  useEffect(() => {
    void loadData(offset);
  }, [loadData, offset]);

  const canGoBack = offset > 0;
  const canGoNext = findings ? findings.offset + findings.limit < findings.total : false;

  return (
    <div className="grid gap-6">
      <div>
        <Link className="text-sm font-medium text-primary" href={`/projects/${params.projectId}`}>
          Back to project
        </Link>
        <h1 className="mt-2 text-2xl font-semibold text-foreground">Scan detail</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          {scan ? `${scan.source} · ${scan.scan_type.toUpperCase()} · generated ${formatDate(scan.generated_at)}` : "Loading scan..."}
        </p>
      </div>
      {error ? <div className="rounded-md bg-red-50 px-3 py-2 text-sm text-red-800">{error}</div> : null}
      <ScanSummaryCards summary={scan?.summary ?? null} />
      <Card>
        <CardHeader>
          <CardTitle>Scan metadata</CardTitle>
        </CardHeader>
        <CardContent>
          {scan ? (
            <dl className="grid gap-3 text-sm md:grid-cols-2">
              <div>
                <dt className="font-medium text-muted-foreground">Backend scan ID</dt>
                <dd className="break-all text-foreground">{scan.id}</dd>
              </div>
              <div>
                <dt className="font-medium text-muted-foreground">Scanner scan ID</dt>
                <dd className="break-all text-foreground">{scan.scanner_scan_id}</dd>
              </div>
              <div>
                <dt className="font-medium text-muted-foreground">Scanner version</dt>
                <dd>{scan.scanner_version}</dd>
              </div>
              <div>
                <dt className="font-medium text-muted-foreground">Raw PII uploaded</dt>
                <dd>{scan.raw_pii_uploaded ? "Yes" : "No"}</dd>
              </div>
            </dl>
          ) : (
            <div className="text-sm text-muted-foreground">Loading metadata...</div>
          )}
        </CardContent>
      </Card>
      <Card>
        <CardHeader>
          <CardTitle>Findings for this scan</CardTitle>
        </CardHeader>
        <CardContent className="grid gap-4">
          <FindingsTable findings={findings?.items ?? []} />
          <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <div className="text-sm text-muted-foreground">
              Showing {findings?.items.length ?? 0} of {findings?.total ?? 0} findings
            </div>
            <div className="flex gap-2">
              <Button disabled={!canGoBack} onClick={() => setOffset(Math.max(offset - limit, 0))} variant="secondary">
                Previous
              </Button>
              <Button disabled={!canGoNext} onClick={() => setOffset(offset + limit)} variant="secondary">
                Next
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
