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
import type { Finding } from "@/lib/types";

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
});
