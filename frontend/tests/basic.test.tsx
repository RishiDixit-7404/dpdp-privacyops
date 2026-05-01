import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import React from "react";

import { ApiError, apiErrorMessage } from "@/lib/api";
import { formatConfidence } from "@/lib/format";
import { RiskBadge } from "@/components/findings/risk-badge";
import { FindingsTable } from "@/components/findings/findings-table";
import { DataRequestStatusBadge } from "@/components/data-requests/data-request-status-badge";
import { DataRequestTypeBadge } from "@/components/data-requests/data-request-type-badge";
import { ConsentStatusBadge } from "@/components/consent/consent-status-badge";
import { ReadinessScansView } from "@/components/readiness-scans/readiness-scans-view";
import type { Finding } from "@/lib/types";
import type { Project, ReadinessScan, ReadinessScanSummary } from "@/lib/types";

const finding: Finding = {
  id: "backend-finding-id",
  scan_id: "backend-scan-id",
  scanner_finding_id: "scanner-finding-id",
  source_type: "json",
  source_name: "sample_logs.jsonl",
  table_or_file: "sample_logs.jsonl",
  field_name: "payload.input_text",
  pii_type: "indian_phone",
  confidence_score: 0.95,
  risk_level: "critical",
  detection_method: "combined",
  masked_examples: ["98******10"],
  sample_count: 10,
  match_count: 4,
  suggested_action: "Add redaction before log, support-ticket, or prompt ingestion.",
  created_at: "2026-04-26T10:00:00Z"
};

const project: Project = {
  id: "project-id",
  organization_id: "org-id",
  name: "Learno AI Tutor",
  description: null,
  created_at: "2026-04-30T10:00:00Z",
  organization: {
    id: "org-id",
    name: "Acme EdTech",
    created_at: "2026-04-30T10:00:00Z"
  }
};

const readinessScan: ReadinessScan = {
  id: "readiness-scan-id",
  project_id: "project-id",
  customer_name: "Acme EdTech",
  customer_segment: "edtech",
  package_name: "DPDP Technical Readiness Scan",
  price_inr: 9999,
  status: "report_ready",
  input_checklist: {
    schema_dump: true,
    masked_csv_exports: true,
    log_samples: true,
    privacy_notice: true,
    third_party_tools: true,
    ai_prompt_samples: true
  },
  notes: "Demo readiness scan using masked metadata and synthetic findings.",
  created_at: "2026-04-30T10:00:00Z",
  updated_at: "2026-04-30T10:00:00Z"
};

const readinessSummary: ReadinessScanSummary = {
  scan_id: "readiness-scan-id",
  package_name: "DPDP Technical Readiness Scan",
  price_inr: 9999,
  status: "report_ready",
  checklist_completion_percentage: 100,
  linked_project: {
    id: "project-id",
    name: "Learno AI Tutor",
    organization_name: "Acme EdTech"
  },
  finding_count: 6,
  high_or_critical_risk_count: 6,
  dsr_request_count: 3,
  consent_event_count: 4,
  evidence_report_available: true,
  next_recommended_action: "Schedule 30-minute walkthrough"
};

describe("dashboard basics", () => {
  it("renders a risk badge label", () => {
    render(<RiskBadge risk="critical" />);

    expect(screen.getByText("CRITICAL")).toBeInTheDocument();
  });

  it("formats confidence as a percentage", () => {
    expect(formatConfidence(0.945)).toBe("95%");
  });

  it("maps duplicate scanner upload errors to a clear message", () => {
    expect(apiErrorMessage(new ApiError(409, "scanner_scan_id already ingested"))).toBe(
      "This scanner output has already been uploaded."
    );
  });

  it("renders data request status and type badges", () => {
    render(
      <>
        <DataRequestStatusBadge status="in_progress" />
        <DataRequestTypeBadge requestType="consent_withdrawal" />
      </>
    );

    expect(screen.getByText("In progress")).toBeInTheDocument();
    expect(screen.getByText("Consent withdrawal")).toBeInTheDocument();
  });

  it("renders consent status badges", () => {
    render(<ConsentStatusBadge status="granted" />);

    expect(screen.getByText("Granted")).toBeInTheDocument();
  });

  it("renders a finding without showing unsupported internal fields", () => {
    render(<FindingsTable findings={[finding]} />);

    expect(screen.getByText("CRITICAL")).toBeInTheDocument();
    expect(screen.getByText("indian phone")).toBeInTheDocument();
    expect(screen.getByText("payload.input_text")).toBeInTheDocument();
    expect(screen.getByText("98******10")).toBeInTheDocument();
    expect(screen.queryByText("scanner-finding-id")).not.toBeInTheDocument();
  });

  it("renders paid readiness scan demo copy and progress", () => {
    render(
      <ReadinessScansView
        draft={{
          project_id: "project-id",
          customer_name: "",
          customer_segment: "edtech",
          status: "draft",
          notes: ""
        }}
        error={null}
        isLoading={false}
        isSubmitting={false}
        onChecklistChange={() => undefined}
        onCreate={() => undefined}
        onDraftChange={() => undefined}
        onStatusChange={() => undefined}
        projects={[project]}
        readinessScans={[readinessScan]}
        success={null}
        summaries={{ "readiness-scan-id": readinessSummary }}
      />
    );

    expect(screen.getByText("DPDP Technical Readiness Scans")).toBeInTheDocument();
    expect(screen.getByText("Rs. 9,999 one-time")).toBeInTheDocument();
    expect(screen.getByText(/We do not want your raw personal data/)).toBeInTheDocument();
    expect(screen.getAllByText("Acme EdTech").length).toBeGreaterThan(0);
    expect(screen.getByText("100% checklist")).toBeInTheDocument();
    expect(screen.getByText("Schedule 30-minute walkthrough")).toBeInTheDocument();
  });
});
