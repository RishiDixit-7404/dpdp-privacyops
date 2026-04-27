"use client";

import Link from "next/link";
import { FormEvent, useCallback, useEffect, useState } from "react";

import { ApiKeyManagement } from "@/components/api-keys/api-key-management";
import { ConsentEventForm } from "@/components/consent/consent-event-form";
import { ConsentEventList } from "@/components/consent/consent-event-list";
import { ConsentStatusChecker } from "@/components/consent/consent-status-checker";
import { ConsentSummaryCards } from "@/components/consent/consent-summary-cards";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { apiErrorMessage, getConsentEvents, getConsentSummary, getProject } from "@/lib/api";
import { consentStatusLabel, consentStatusOptions } from "@/lib/format";
import type { ConsentEventFilters, ConsentEventListResponse, ConsentStatus, ConsentSummaryResponse, Project } from "@/lib/types";

export default function ProjectConsentPage({ params }: { params: { projectId: string } }) {
  const [project, setProject] = useState<Project | null>(null);
  const [events, setEvents] = useState<ConsentEventListResponse | null>(null);
  const [summary, setSummary] = useState<ConsentSummaryResponse | null>(null);
  const [filters, setFilters] = useState<ConsentEventFilters>({ limit: 100, offset: 0 });
  const [draftFilters, setDraftFilters] = useState<ConsentEventFilters>({ limit: 100, offset: 0 });
  const [writeApiKey, setWriteApiKey] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const loadData = useCallback(async (nextFilters: ConsentEventFilters) => {
    setError(null);
    setIsLoading(true);
    try {
      const [projectResponse, eventResponse, summaryResponse] = await Promise.all([
        getProject(params.projectId),
        getConsentEvents(params.projectId, nextFilters),
        getConsentSummary(params.projectId)
      ]);
      setProject(projectResponse);
      setEvents(eventResponse);
      setSummary(summaryResponse);
    } catch (requestError) {
      setError(apiErrorMessage(requestError));
    } finally {
      setIsLoading(false);
    }
  }, [params.projectId]);

  useEffect(() => {
    void loadData(filters);
  }, [filters, loadData]);

  function applyFilters(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setFilters({ ...draftFilters, limit: 100, offset: 0 });
  }

  const canGoBack = (events?.offset ?? 0) > 0;
  const canGoNext = events ? events.offset + events.limit < events.total : false;

  return (
    <div className="grid gap-6">
      <div>
        <Link className="text-sm font-medium text-primary" href={`/projects/${params.projectId}`}>
          Back to project
        </Link>
        <h1 className="mt-2 text-2xl font-semibold text-foreground">Consent Events</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Append-only ledger of granted and withdrawn consent by purpose{project ? ` for ${project.name}.` : "."}
        </p>
      </div>

      {error ? <div className="rounded-md bg-red-50 px-3 py-2 text-sm text-red-800">{error}</div> : null}

      <ConsentSummaryCards summary={summary} />

      <Card>
        <CardHeader>
          <CardTitle>API keys</CardTitle>
        </CardHeader>
        <CardContent className="grid gap-4">
          <div className="text-sm text-muted-foreground">
            Local MVP admin controls for consent write API keys. This protects consent event writes but is not full user login.
          </div>
          <ApiKeyManagement onCreated={setWriteApiKey} projectId={params.projectId} />
        </CardContent>
      </Card>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Record consent event</CardTitle>
          </CardHeader>
          <CardContent className="grid gap-4">
            <label className="space-y-1 text-sm">
              <span className="text-xs font-medium text-muted-foreground">Project API key for this browser session</span>
              <Input
                onChange={(event) => setWriteApiKey(event.target.value)}
                placeholder="dpdp_live_..."
                type="password"
                value={writeApiKey}
              />
            </label>
            <ConsentEventForm
              apiKey={writeApiKey}
              onCreated={() => {
                void loadData(filters);
              }}
              projectId={params.projectId}
            />
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Check current status</CardTitle>
          </CardHeader>
          <CardContent>
            <ConsentStatusChecker projectId={params.projectId} />
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Event ledger</CardTitle>
        </CardHeader>
        <CardContent className="grid gap-4">
          <form className="grid gap-3 md:grid-cols-[1fr_1fr_160px_auto]" onSubmit={applyFilters}>
            <label className="space-y-1 text-sm">
              <span className="text-xs font-medium text-muted-foreground">External user ID</span>
              <Input
                onChange={(event) => setDraftFilters((current) => ({ ...current, external_user_id: event.target.value || undefined }))}
                value={draftFilters.external_user_id ?? ""}
              />
            </label>
            <label className="space-y-1 text-sm">
              <span className="text-xs font-medium text-muted-foreground">Purpose</span>
              <Input
                onChange={(event) => setDraftFilters((current) => ({ ...current, purpose: event.target.value || undefined }))}
                value={draftFilters.purpose ?? ""}
              />
            </label>
            <label className="space-y-1 text-sm">
              <span className="text-xs font-medium text-muted-foreground">Status</span>
              <Select
                value={draftFilters.status ?? "all"}
                onChange={(event) =>
                  setDraftFilters((current) => ({
                    ...current,
                    status: event.target.value === "all" ? undefined : (event.target.value as ConsentStatus)
                  }))
                }
              >
                <option value="all">All statuses</option>
                {consentStatusOptions.map((status) => (
                  <option key={status} value={status}>
                    {consentStatusLabel(status)}
                  </option>
                ))}
              </Select>
            </label>
            <div className="flex items-end gap-2">
              <Button className="w-full" type="submit" variant="secondary">
                Apply
              </Button>
              <Button
                className="w-full"
                onClick={() => {
                  setDraftFilters({ limit: 100, offset: 0 });
                  setFilters({ limit: 100, offset: 0 });
                }}
                variant="ghost"
              >
                Reset
              </Button>
            </div>
          </form>
          {isLoading ? <div className="text-sm text-muted-foreground">Loading consent events...</div> : null}
          <ConsentEventList events={events?.items ?? []} />
          <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <div className="text-sm text-muted-foreground">
              Showing {events?.items.length ?? 0} of {events?.total ?? 0} events
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
