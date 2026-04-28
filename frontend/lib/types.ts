export type ScanType = "csv" | "postgres" | "json";
export type SourceType = "csv" | "postgres" | "json";
export type RiskLevel = "low" | "medium" | "high" | "critical";
export type DetectionMethod = "column_name" | "regex_value" | "combined";
export type DataRequestType = "access" | "correction" | "deletion" | "consent_withdrawal" | "grievance";
export type DataRequestStatus = "new" | "verifying" | "in_progress" | "completed" | "rejected";
export type DataRequestAuditEventType =
  | "created"
  | "status_changed"
  | "note_added"
  | "assigned"
  | "due_date_changed"
  | "completed"
  | "rejected";
export type ConsentStatus = "granted" | "withdrawn";

export type PiiType =
  | "email"
  | "indian_phone"
  | "pan"
  | "aadhaar"
  | "upi_id"
  | "date_of_birth"
  | "person_name"
  | "address"
  | "student_or_child_data"
  | "health_data"
  | "employment_data"
  | "financial_data"
  | "authentication_secret"
  | "free_text_possible_pii";

export interface Organization {
  id: string;
  name: string;
  created_at: string;
}

export interface Project {
  id: string;
  organization_id: string;
  name: string;
  description: string | null;
  created_at: string;
  organization: Organization;
}

export interface ProjectCreateInput {
  organization_name: string;
  project_name: string;
  description?: string | null;
}

export type MembershipRole = "owner" | "admin" | "member";

export interface AuthUser {
  id: string;
  email: string;
  full_name: string | null;
  created_at: string;
  disabled_at: string | null;
}

export interface AuthOrganization extends Organization {
  role: MembershipRole;
}

export interface AuthMeResponse {
  user: AuthUser;
  organizations: AuthOrganization[];
}

export interface AuthTokenResponse extends AuthMeResponse {
  access_token: string;
  token_type: "bearer";
}

export interface RegisterInput {
  email: string;
  password: string;
  full_name?: string | null;
  organization_name?: string | null;
}

export interface LoginInput {
  email: string;
  password: string;
}

export interface ApiKey {
  id: string;
  project_id: string;
  name: string;
  key_prefix: string;
  created_at: string;
  revoked_at: string | null;
  last_used_at: string | null;
}

export interface ApiKeyCreateResponse extends ApiKey {
  api_key: string;
}

export interface ScanSummary {
  total_findings: number;
  counts_by_risk_level: Record<RiskLevel, number>;
  counts_by_pii_type: Record<string, number>;
  critical_count: number;
  high_count: number;
}

export interface Scan {
  id: string;
  project_id: string;
  scanner_scan_id: string;
  scanner_version: string;
  scan_type: ScanType;
  source: string;
  generated_at: string;
  raw_pii_uploaded: boolean;
  created_at: string;
}

export interface ScanDetail extends Scan {
  summary: ScanSummary;
}

export interface ScannerUploadResponse extends Scan {
  summary: ScanSummary;
}

export interface Finding {
  id: string;
  scan_id: string;
  scanner_finding_id: string;
  source_type: SourceType;
  source_name: string;
  table_or_file: string;
  field_name: string;
  pii_type: PiiType | string;
  confidence_score: number;
  risk_level: RiskLevel;
  detection_method: DetectionMethod;
  masked_examples: string[];
  sample_count: number;
  match_count: number;
  suggested_action: string;
  created_at: string;
}

export interface FindingListResponse {
  items: Finding[];
  total: number;
  limit: number;
  offset: number;
}

export interface FindingFilters {
  risk_level?: RiskLevel;
  pii_type?: PiiType | string;
  source_type?: SourceType;
  scan_id?: string;
  limit?: number;
  offset?: number;
}

export interface DataRequest {
  id: string;
  project_id: string;
  request_type: DataRequestType;
  status: DataRequestStatus;
  requester_name: string | null;
  requester_email: string;
  requester_identifier: string | null;
  request_details: string | null;
  due_date: string | null;
  assigned_to: string | null;
  created_at: string;
  updated_at: string;
  completed_at: string | null;
}

export interface DataRequestNote {
  id: string;
  data_request_id: string;
  note: string;
  created_by: string | null;
  created_at: string;
}

export interface DataRequestAuditEvent {
  id: string;
  data_request_id: string;
  event_type: DataRequestAuditEventType;
  message: string;
  metadata: Record<string, unknown> | null;
  created_at: string;
}

export interface DataRequestDetail extends DataRequest {
  notes: DataRequestNote[];
  audit_events: DataRequestAuditEvent[];
}

export interface DataRequestListResponse {
  items: DataRequest[];
  total: number;
  limit: number;
  offset: number;
}

export interface DataRequestFilters {
  status?: DataRequestStatus;
  request_type?: DataRequestType;
  limit?: number;
  offset?: number;
}

export interface DataRequestCreateInput {
  request_type: DataRequestType;
  requester_name?: string | null;
  requester_email: string;
  requester_identifier?: string | null;
  request_details?: string | null;
  due_date?: string | null;
  assigned_to?: string | null;
}

export interface DataRequestUpdateInput {
  status?: DataRequestStatus;
  assigned_to?: string | null;
  due_date?: string | null;
  request_details?: string | null;
}

export interface DataRequestNoteCreateInput {
  note: string;
  created_by?: string | null;
}

export interface PublicDataRequestConfirmation {
  request_id: string;
  status: "new";
  message: string;
}

export interface ConsentEvent {
  id: string;
  project_id: string;
  external_user_id: string;
  purpose: string;
  status: ConsentStatus;
  notice_version: string;
  source: string | null;
  occurred_at: string;
  metadata: Record<string, unknown> | null;
  created_at: string;
}

export interface ConsentEventCreate {
  external_user_id: string;
  purpose: string;
  status: ConsentStatus;
  notice_version: string;
  source?: string | null;
  occurred_at: string;
  metadata?: Record<string, unknown> | null;
}

export interface ConsentEventFilters {
  external_user_id?: string;
  purpose?: string;
  status?: ConsentStatus;
  limit?: number;
  offset?: number;
}

export interface ConsentEventListResponse {
  items: ConsentEvent[];
  total: number;
  limit: number;
  offset: number;
}

export interface ConsentStatusResponse {
  project_id: string;
  external_user_id: string;
  purpose: string;
  current_status: ConsentStatus;
  notice_version: string;
  source: string | null;
  occurred_at: string;
  latest_event_id: string;
}

export interface ConsentPurposeSummary {
  purpose: string;
  granted_count: number;
  withdrawn_count: number;
  latest_event_at: string | null;
}

export interface ConsentSummaryResponse {
  total_events: number;
  granted_count: number;
  withdrawn_count: number;
  purposes: ConsentPurposeSummary[];
}

export interface ReportProjectSummary {
  id: string;
  name: string;
  description: string | null;
  organization_name: string;
  created_at: string;
}

export interface EvidenceScanSummary {
  scan_count: number;
  latest_scan_id: string | null;
  latest_scan_source: string | null;
  latest_scan_type: string | null;
  latest_scan_generated_at: string | null;
}

export interface RiskSummary {
  total_findings: number;
  counts_by_risk_level: Record<RiskLevel, number>;
  critical_count: number;
  high_count: number;
  highest_risk_level: RiskLevel | null;
}

export interface DataInventorySummary {
  counts_by_pii_type: Record<string, number>;
  counts_by_source_type: Record<string, number>;
  sources_scanned: string[];
  scan_types: string[];
  latest_scan_generated_at: string | null;
}

export interface ReportTopRisk {
  risk_level: RiskLevel;
  pii_type: string;
  source_type: SourceType;
  source_name: string;
  field_name: string;
  confidence_score: number;
  masked_examples: string[];
  suggested_action: string;
}

export interface DsrSummary {
  total_requests: number;
  counts_by_status: Record<DataRequestStatus, number>;
  counts_by_type: Record<string, number>;
  open_requests: number;
  overdue_requests: number;
  latest_request_created_at: string | null;
}

export interface ConsentReportPurposeSummary {
  purpose: string;
  granted_count: number;
  withdrawn_count: number;
  latest_event_at: string | null;
}

export interface ConsentReportSummary {
  total_events: number;
  granted_count: number;
  withdrawn_count: number;
  purposes: ConsentReportPurposeSummary[];
  latest_event_at: string | null;
}

export interface RemediationAction {
  priority: RiskLevel;
  title: string;
  description: string;
  affected_fields_count: number;
  related_pii_types: string[];
  related_sources: string[];
}

export interface RemediationSummary {
  total_recommended_actions: number;
  critical_actions: number;
  high_priority_actions: number;
  actions: RemediationAction[];
}

export type ReadinessGapArea = "data_discovery" | "dsr" | "consent" | "retention" | "security" | "ai_or_logs";

export interface ReadinessGap {
  severity: RiskLevel;
  area: ReadinessGapArea;
  message: string;
  suggested_next_step: string;
}

export interface EvidenceReportResponse {
  project: ReportProjectSummary;
  generated_at: string;
  report_version: "0.1.0";
  disclaimer: string;
  executive_summary: string;
  scan_summary: EvidenceScanSummary;
  risk_summary: RiskSummary;
  data_inventory_summary: DataInventorySummary;
  top_risks: ReportTopRisk[];
  dsr_summary: DsrSummary;
  consent_summary: ConsentReportSummary;
  remediation_summary: RemediationSummary;
  readiness_gaps: ReadinessGap[];
}
