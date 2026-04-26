"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";

import { DataRequestFilters } from "@/components/data-requests/data-request-filters";
import { DataRequestForm } from "@/components/data-requests/data-request-form";
import { DataRequestList } from "@/components/data-requests/data-request-list";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { apiErrorMessage, getProject, getProjectDataRequests } from "@/lib/api";
import type { DataRequestFilters as DataRequestFiltersType, DataRequestListResponse, Project } from "@/lib/types";

export default function ProjectRequestsPage({ params }: { params: { projectId: string } }) {
  const [project, setProject] = useState<Project | null>(null);
  const [requests, setRequests] = useState<DataRequestListResponse | null>(null);
  const [filters, setFilters] = useState<DataRequestFiltersType>({ limit: 100, offset: 0 });
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [success, setSuccess] = useState<string | null>(null);

  const loadData = useCallback(async (nextFilters: DataRequestFiltersType) => {
    setError(null);
    setIsLoading(true);
    try {
      const [projectResponse, requestResponse] = await Promise.all([
        getProject(params.projectId),
        getProjectDataRequests(params.projectId, nextFilters)
      ]);
      setProject(projectResponse);
      setRequests(requestResponse);
    } catch (requestError) {
      setError(apiErrorMessage(requestError));
    } finally {
      setIsLoading(false);
    }
  }, [params.projectId]);

  useEffect(() => {
    void loadData(filters);
  }, [filters, loadData]);

  const canGoBack = (requests?.offset ?? 0) > 0;
  const canGoNext = requests ? requests.offset + requests.limit < requests.total : false;

  return (
    <div className="grid gap-6">
      <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
        <div>
          <Link className="text-sm font-medium text-primary" href={`/projects/${params.projectId}`}>
            Back to project
          </Link>
          <h1 className="mt-2 text-2xl font-semibold text-foreground">User Data Requests</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Track access, correction, deletion, consent withdrawal, and grievance requests
            {project ? ` for ${project.name}.` : "."}
          </p>
        </div>
        <Link href={`/public/projects/${params.projectId}/privacy-request`}>
          <Button variant="secondary">Open public form</Button>
        </Link>
      </div>

      {error ? <div className="rounded-md bg-red-50 px-3 py-2 text-sm text-red-800">{error}</div> : null}
      {success ? <div className="rounded-md bg-emerald-50 px-3 py-2 text-sm text-emerald-900">{success}</div> : null}

      <Card>
        <CardHeader>
          <CardTitle>Create request</CardTitle>
        </CardHeader>
        <CardContent>
          <DataRequestForm
            onCreated={(created) => {
              setSuccess(`Created request ${created.id}.`);
              void loadData(filters);
            }}
            projectId={params.projectId}
          />
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Request inbox</CardTitle>
        </CardHeader>
        <CardContent className="grid gap-4">
          <DataRequestFilters filters={filters} onChange={(nextFilters) => setFilters({ limit: 100, offset: 0, ...nextFilters })} />
          {isLoading ? <div className="text-sm text-muted-foreground">Loading requests...</div> : null}
          <DataRequestList dataRequests={requests?.items ?? []} projectId={params.projectId} />
          <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <div className="text-sm text-muted-foreground">
              Showing {requests?.items.length ?? 0} of {requests?.total ?? 0} requests
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
    </div>
  );
}
