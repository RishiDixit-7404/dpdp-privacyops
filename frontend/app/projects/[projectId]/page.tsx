"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";

import { FindingsFilters } from "@/components/findings/findings-filters";
import { FindingsTable } from "@/components/findings/findings-table";
import { ScannerUpload } from "@/components/scans/scanner-upload";
import { ScanList } from "@/components/scans/scan-list";
import { ScanSummaryCards } from "@/components/scans/scan-summary-cards";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { apiErrorMessage, getProject, getProjectFindings, getProjectScans, getScan } from "@/lib/api";
import { formatDate } from "@/lib/format";
import type { FindingFilters, FindingListResponse, Project, Scan, ScanSummary } from "@/lib/types";

export default function ProjectDetailPage({ params }: { params: { projectId: string } }) {
  const [project, setProject] = useState<Project | null>(null);
  const [scans, setScans] = useState<Scan[]>([]);
  const [findings, setFindings] = useState<FindingListResponse | null>(null);
  const [latestSummary, setLatestSummary] = useState<ScanSummary | null>(null);
  const [filters, setFilters] = useState<FindingFilters>({ limit: 100, offset: 0 });
  const [isLoading, setIsLoading] = useState(true);
  const [isFindingsLoading, setIsFindingsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadProjectData = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const [projectResponse, scanResponse] = await Promise.all([
        getProject(params.projectId),
        getProjectScans(params.projectId)
      ]);
      setProject(projectResponse);
      setScans(scanResponse);
      if (scanResponse[0]) {
        const detail = await getScan(scanResponse[0].id);
        setLatestSummary(detail.summary);
      } else {
        setLatestSummary(null);
      }
    } catch (requestError) {
      setError(apiErrorMessage(requestError));
    } finally {
      setIsLoading(false);
    }
  }, [params.projectId]);

  const loadFindings = useCallback(async (nextFilters: FindingFilters) => {
    setIsFindingsLoading(true);
    try {
      setFindings(await getProjectFindings(params.projectId, nextFilters));
    } catch (requestError) {
      setError(apiErrorMessage(requestError));
    } finally {
      setIsFindingsLoading(false);
    }
  }, [params.projectId]);

  useEffect(() => {
    void loadProjectData();
  }, [loadProjectData]);

  useEffect(() => {
    void loadFindings(filters);
  }, [filters, loadFindings]);

  function updateFilters(nextFilters: FindingFilters) {
    setFilters({ limit: 100, offset: 0, ...nextFilters });
  }

  const canGoBack = (findings?.offset ?? 0) > 0;
  const canGoNext = findings ? findings.offset + findings.limit < findings.total : false;

  return (
    <div className="grid gap-6">
      <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
        <div>
          <Link className="text-sm font-medium text-primary" href="/projects">
            Back to projects
          </Link>
          <h1 className="mt-2 text-2xl font-semibold text-foreground">{project?.name ?? "Project"}</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            {project ? `${project.organization.name} · created ${formatDate(project.created_at)}` : "Loading project..."}
          </p>
        </div>
        <Link href="#findings">
          <Button variant="secondary">View findings inventory</Button>
        </Link>
      </div>
      {error ? <div className="rounded-md bg-red-50 px-3 py-2 text-sm text-red-800">{error}</div> : null}
      <section className="grid gap-4">
        <h2 className="text-lg font-semibold text-foreground">Latest scan summary</h2>
        <ScanSummaryCards summary={latestSummary} />
      </section>
      <div className="grid gap-6 lg:grid-cols-[420px_1fr]">
        <ScannerUpload
          onUploaded={() => {
            void loadProjectData();
            void loadFindings(filters);
          }}
          projectId={params.projectId}
        />
        <ScanList isLoading={isLoading} projectId={params.projectId} scans={scans} />
      </div>
      <section className="grid gap-4" id="findings">
        <Card>
          <CardHeader>
            <CardTitle>Findings inventory</CardTitle>
          </CardHeader>
          <CardContent className="grid gap-4">
            <FindingsFilters filters={filters} onChange={updateFilters} scans={scans} />
            {isFindingsLoading ? <div className="text-sm text-muted-foreground">Loading findings...</div> : null}
            <FindingsTable findings={findings?.items ?? []} />
            <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
              <div className="text-sm text-muted-foreground">
                Showing {findings?.items.length ?? 0} of {findings?.total ?? 0} findings
              </div>
              <div className="flex gap-2">
                <Button
                  disabled={!canGoBack}
                  onClick={() => setFilters((current) => ({ ...current, offset: Math.max((current.offset ?? 0) - 100, 0) }))}
                  variant="secondary"
                >
                  Previous
                </Button>
                <Button
                  disabled={!canGoNext}
                  onClick={() => setFilters((current) => ({ ...current, offset: (current.offset ?? 0) + 100 }))}
                  variant="secondary"
                >
                  Next
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      </section>
    </div>
  );
}
