"use client";

import Link from "next/link";
import type { FormEvent } from "react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { formatEnumLabel } from "@/lib/format";
import type {
  CustomerSegment,
  Project,
  ReadinessScan,
  ReadinessScanChecklist,
  ReadinessScanCreateInput,
  ReadinessScanStatus,
  ReadinessScanSummary
} from "@/lib/types";

export const customerSegmentOptions: CustomerSegment[] = [
  "edtech",
  "healthtech",
  "hrtech",
  "ai_saas",
  "b2b_saas",
  "other"
];

export const readinessStatusOptions: ReadinessScanStatus[] = [
  "draft",
  "inputs_requested",
  "inputs_received",
  "scanning",
  "report_ready",
  "walkthrough_done",
  "converted_to_subscription",
  "closed_lost"
];

export const checklistItems: Array<{ key: keyof ReadinessScanChecklist; label: string }> = [
  { key: "schema_dump", label: "Schema dump without data" },
  { key: "masked_csv_exports", label: "Masked CSV/sample exports" },
  { key: "log_samples", label: "Masked log samples" },
  { key: "privacy_notice", label: "Privacy policy or notice" },
  { key: "third_party_tools", label: "Third-party tools list" },
  { key: "ai_prompt_samples", label: "Masked AI prompt/log samples" }
];

interface ReadinessScansViewProps {
  projects: Project[];
  readinessScans: ReadinessScan[];
  summaries: Record<string, ReadinessScanSummary>;
  draft: ReadinessScanCreateInput;
  error: string | null;
  success: string | null;
  isLoading: boolean;
  isSubmitting: boolean;
  onDraftChange: (draft: ReadinessScanCreateInput) => void;
  onCreate: () => void;
  onStatusChange: (scan: ReadinessScan, status: ReadinessScanStatus) => void;
  onChecklistChange: (scan: ReadinessScan, key: keyof ReadinessScanChecklist, checked: boolean) => void;
}

export function checklistProgress(checklist: ReadinessScanChecklist): number {
  const values = Object.values(checklist);
  return Math.round((values.filter(Boolean).length / values.length) * 100);
}

export function ReadinessScansView({
  draft,
  error,
  isLoading,
  isSubmitting,
  onChecklistChange,
  onCreate,
  onDraftChange,
  onStatusChange,
  projects,
  readinessScans,
  success,
  summaries
}: ReadinessScansViewProps) {
  const projectById = new Map(projects.map((project) => [project.id, project]));

  function submitForm(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    onCreate();
  }

  return (
    <div className="grid gap-6">
      <div>
        <h1 className="text-2xl font-semibold text-foreground">DPDP Technical Readiness Scans</h1>
        <p className="mt-2 max-w-3xl text-sm text-muted-foreground">
          Run a paid technical scan that shows where personal data exists, what is risky, and what needs fixing.
        </p>
      </div>

      <section className="grid gap-4 lg:grid-cols-[360px_1fr]">
        <Card>
          <CardHeader>
            <CardTitle>Rs. 9,999 one-time</CardTitle>
          </CardHeader>
          <CardContent className="grid gap-3 text-sm text-muted-foreground">
            <p className="font-medium text-foreground">5-day technical readiness scan</p>
            <p>
              Includes personal-data inventory, risk review, DSR/consent gap check, evidence report, and 30-minute
              walkthrough.
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Trust note</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">
              We do not want your raw personal data. The scanner runs inside your environment and sends only metadata,
              masked examples, confidence scores, and risk tags.
            </p>
          </CardContent>
        </Card>
      </section>

      {error ? <div className="rounded-md bg-red-50 px-3 py-2 text-sm text-red-800">{error}</div> : null}
      {success ? <div className="rounded-md bg-emerald-50 px-3 py-2 text-sm text-emerald-900">{success}</div> : null}

      <Card>
        <CardHeader>
          <CardTitle>Create readiness scan</CardTitle>
        </CardHeader>
        <CardContent>
          <form className="grid gap-4" onSubmit={submitForm}>
            <div className="grid gap-3 md:grid-cols-2">
              <label className="space-y-1 text-sm">
                <span className="text-xs font-medium text-muted-foreground">Customer name</span>
                <Input
                  onChange={(event) => onDraftChange({ ...draft, customer_name: event.target.value })}
                  required
                  value={draft.customer_name}
                />
              </label>
              <label className="space-y-1 text-sm">
                <span className="text-xs font-medium text-muted-foreground">Project</span>
                <Select
                  onChange={(event) => onDraftChange({ ...draft, project_id: event.target.value })}
                  required
                  value={draft.project_id}
                >
                  <option value="">Choose project</option>
                  {projects.map((project) => (
                    <option key={project.id} value={project.id}>
                      {project.name}
                    </option>
                  ))}
                </Select>
              </label>
              <label className="space-y-1 text-sm">
                <span className="text-xs font-medium text-muted-foreground">Segment</span>
                <Select
                  onChange={(event) =>
                    onDraftChange({ ...draft, customer_segment: event.target.value as CustomerSegment })
                  }
                  value={draft.customer_segment}
                >
                  {customerSegmentOptions.map((segment) => (
                    <option key={segment} value={segment}>
                      {formatEnumLabel(segment)}
                    </option>
                  ))}
                </Select>
              </label>
              <label className="space-y-1 text-sm">
                <span className="text-xs font-medium text-muted-foreground">Status</span>
                <Select
                  onChange={(event) => onDraftChange({ ...draft, status: event.target.value as ReadinessScanStatus })}
                  value={draft.status ?? "draft"}
                >
                  {readinessStatusOptions.map((status) => (
                    <option key={status} value={status}>
                      {formatEnumLabel(status)}
                    </option>
                  ))}
                </Select>
              </label>
            </div>
            <label className="space-y-1 text-sm">
              <span className="text-xs font-medium text-muted-foreground">Notes</span>
              <Textarea
                maxLength={5000}
                onChange={(event) => onDraftChange({ ...draft, notes: event.target.value || null })}
                placeholder="Use safe operational notes only. Do not paste raw personal data."
                value={draft.notes ?? ""}
              />
            </label>
            <Button className="w-full md:w-fit" disabled={isSubmitting || !draft.project_id} type="submit">
              {isSubmitting ? "Creating..." : "Create readiness scan"}
            </Button>
          </form>
        </CardContent>
      </Card>

      <section className="grid gap-4">
        <h2 className="text-lg font-semibold text-foreground">Scan packages</h2>
        {isLoading ? <div className="text-sm text-muted-foreground">Loading readiness scans...</div> : null}
        {!isLoading && readinessScans.length === 0 ? (
          <div className="rounded-md border border-border bg-surface p-4 text-sm text-muted-foreground">
            No readiness scans yet.
          </div>
        ) : null}
        {readinessScans.map((scan) => {
          const project = projectById.get(scan.project_id);
          const summary = summaries[scan.id];
          const progress = summary?.checklist_completion_percentage ?? checklistProgress(scan.input_checklist);
          return (
            <Card key={scan.id}>
              <CardHeader>
                <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
                  <div>
                    <CardTitle>{scan.customer_name}</CardTitle>
                    <p className="mt-1 text-sm text-muted-foreground">
                      {project?.name ?? "Project"} · {formatEnumLabel(scan.customer_segment)}
                    </p>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    <Badge>{formatEnumLabel(scan.status)}</Badge>
                    <Badge>Rs. {scan.price_inr.toLocaleString("en-IN")}</Badge>
                    <Badge>{progress}% checklist</Badge>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="grid gap-5">
                <div className="grid gap-4 md:grid-cols-4">
                  <Metric label="Findings" value={summary?.finding_count ?? 0} />
                  <Metric label="High/Critical" value={summary?.high_or_critical_risk_count ?? 0} />
                  <Metric label="DSR records" value={summary?.dsr_request_count ?? 0} />
                  <Metric label="Consent events" value={summary?.consent_event_count ?? 0} />
                </div>

                <div className="grid gap-3 md:grid-cols-[240px_1fr]">
                  <label className="space-y-1 text-sm">
                    <span className="text-xs font-medium text-muted-foreground">Status</span>
                    <Select
                      onChange={(event) => onStatusChange(scan, event.target.value as ReadinessScanStatus)}
                      value={scan.status}
                    >
                      {readinessStatusOptions.map((status) => (
                        <option key={status} value={status}>
                          {formatEnumLabel(status)}
                        </option>
                      ))}
                    </Select>
                  </label>
                  <div className="rounded-md border border-border bg-muted p-3 text-sm">
                    <div className="font-medium text-foreground">Next action</div>
                    <div className="mt-1 text-muted-foreground">
                      {summary?.next_recommended_action ?? "Request safe customer inputs"}
                    </div>
                  </div>
                </div>

                <div className="grid gap-2 md:grid-cols-2">
                  {checklistItems.map((item) => (
                    <label
                      className="flex min-h-10 items-center gap-3 rounded-md border border-border px-3 py-2 text-sm"
                      key={item.key}
                    >
                      <input
                        checked={scan.input_checklist[item.key]}
                        onChange={(event) => onChecklistChange(scan, item.key, event.target.checked)}
                        type="checkbox"
                      />
                      <span>{item.label}</span>
                    </label>
                  ))}
                </div>

                {scan.notes ? <p className="text-sm text-muted-foreground">{scan.notes}</p> : null}

                <div className="flex flex-wrap gap-2">
                  <Link href={`/projects/${scan.project_id}`}>
                    <Button variant="secondary">Open project dashboard</Button>
                  </Link>
                  <Link href={`/projects/${scan.project_id}/evidence-report`}>
                    <Button variant="secondary">Open evidence report</Button>
                  </Link>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </section>
    </div>
  );
}

function Metric({ label, value }: { label: string; value: number }) {
  return (
    <div className="rounded-md border border-border p-3">
      <div className="text-xs font-medium text-muted-foreground">{label}</div>
      <div className="mt-1 text-xl font-semibold text-foreground">{value}</div>
    </div>
  );
}
