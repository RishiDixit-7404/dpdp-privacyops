"use client";

import { useCallback, useEffect, useState } from "react";

import { ReadinessScansView } from "@/components/readiness-scans/readiness-scans-view";
import {
  apiErrorMessage,
  createReadinessScan,
  getProjects,
  getReadinessScans,
  getReadinessScanSummary,
  updateReadinessScan,
  updateReadinessScanChecklist
} from "@/lib/api";
import type {
  Project,
  ReadinessScan,
  ReadinessScanChecklist,
  ReadinessScanCreateInput,
  ReadinessScanStatus,
  ReadinessScanSummary
} from "@/lib/types";

const emptyDraft: ReadinessScanCreateInput = {
  project_id: "",
  customer_name: "",
  customer_segment: "edtech",
  status: "draft",
  notes: ""
};

export default function ReadinessScansPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [readinessScans, setReadinessScans] = useState<ReadinessScan[]>([]);
  const [summaries, setSummaries] = useState<Record<string, ReadinessScanSummary>>({});
  const [draft, setDraft] = useState<ReadinessScanCreateInput>(emptyDraft);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const loadData = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const [projectResponse, scanResponse] = await Promise.all([getProjects(), getReadinessScans()]);
      setProjects(projectResponse);
      setReadinessScans(scanResponse);
      if (!draft.project_id && projectResponse[0]) {
        setDraft((current) => ({ ...current, project_id: projectResponse[0].id }));
      }
      const summaryEntries = await Promise.all(
        scanResponse.map(async (scan) => [scan.id, await getReadinessScanSummary(scan.id)] as const)
      );
      setSummaries(Object.fromEntries(summaryEntries));
    } catch (requestError) {
      setError(apiErrorMessage(requestError));
    } finally {
      setIsLoading(false);
    }
  }, [draft.project_id]);

  useEffect(() => {
    void loadData();
  }, [loadData]);

  async function handleCreate() {
    setError(null);
    setSuccess(null);
    setIsSubmitting(true);
    try {
      await createReadinessScan({
        ...draft,
        notes: draft.notes || null
      });
      setDraft({ ...emptyDraft, project_id: projects[0]?.id ?? "" });
      setSuccess("Readiness scan created.");
      await loadData();
    } catch (requestError) {
      setError(apiErrorMessage(requestError));
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleStatusChange(scan: ReadinessScan, status: ReadinessScanStatus) {
    setError(null);
    setSuccess(null);
    try {
      await updateReadinessScan(scan.id, { status });
      await loadData();
    } catch (requestError) {
      setError(apiErrorMessage(requestError));
    }
  }

  async function handleChecklistChange(
    scan: ReadinessScan,
    key: keyof ReadinessScanChecklist,
    checked: boolean
  ) {
    setError(null);
    setSuccess(null);
    try {
      await updateReadinessScanChecklist(scan.id, { [key]: checked });
      await loadData();
    } catch (requestError) {
      setError(apiErrorMessage(requestError));
    }
  }

  return (
    <ReadinessScansView
      draft={draft}
      error={error}
      isLoading={isLoading}
      isSubmitting={isSubmitting}
      onChecklistChange={handleChecklistChange}
      onCreate={handleCreate}
      onDraftChange={setDraft}
      onStatusChange={handleStatusChange}
      projects={projects}
      readinessScans={readinessScans}
      success={success}
      summaries={summaries}
    />
  );
}
