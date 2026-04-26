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
