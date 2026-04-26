import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import React from "react";

import { ApiError, apiErrorMessage } from "@/lib/api";
import { formatConfidence } from "@/lib/format";
import { RiskBadge } from "@/components/findings/risk-badge";
import { FindingsTable } from "@/components/findings/findings-table";
import { DataRequestStatusBadge } from "@/components/data-requests/data-request-status-badge";
import { DataRequestTypeBadge } from "@/components/data-requests/data-request-type-badge";
import { ConsentStatusBadge } from "@/components/consent/consent-status-badge";
import { PrintReportButton } from "@/components/reports/print-report-button";
import { ReadinessGapsSection } from "@/components/reports/readiness-gaps-section";
import { ReportDisclaimer } from "@/components/reports/report-disclaimer";
import { RiskSummarySection } from "@/components/reports/risk-summary-section";
import type { Finding, ReadinessGap, RiskSummary } from "@/lib/types";

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

const riskSummary: RiskSummary = {
  total_findings: 7,
  counts_by_risk_level: {
    critical: 2,
    high: 3,
    medium: 1,
    low: 1
  },
  critical_count: 2,
  high_count: 3,
  highest_risk_level: "critical"
};

const readinessGaps: ReadinessGap[] = [
  {
    severity: "high",
    area: "consent",
    message: "No consent events have been recorded.",
    suggested_next_step: "Record consent events for key purposes."
  }
];

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

  it("renders the report disclaimer", () => {
    render(
      <ReportDisclaimer text="This report is technical evidence of discovered data flows, risks, and workflow status. It is not a legal compliance certificate." />
    );

    expect(screen.getByText(/not a legal compliance certificate/i)).toBeInTheDocument();
  });

  it("renders risk summary counts", () => {
    render(<RiskSummarySection summary={riskSummary} />);

    expect(screen.getByText("Risk Summary")).toBeInTheDocument();
    expect(screen.getByText("2")).toBeInTheDocument();
    expect(screen.getByText("3")).toBeInTheDocument();
  });

  it("renders readiness gap severity and message", () => {
    render(<ReadinessGapsSection gaps={readinessGaps} />);

    expect(screen.getByText("HIGH")).toBeInTheDocument();
    expect(screen.getByText("No consent events have been recorded.")).toBeInTheDocument();
  });

  it("print button calls window.print", async () => {
    const printMock = vi.fn();
    Object.defineProperty(window, "print", { value: printMock, writable: true });
    render(<PrintReportButton />);

    await userEvent.click(screen.getByText("Print report"));

    expect(printMock).toHaveBeenCalledOnce();
  });
});
