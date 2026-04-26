export type ScanType = "csv" | "postgres" | "json";
export type SourceType = "csv" | "postgres" | "json";
export type RiskLevel = "low" | "medium" | "high" | "critical";
export type DetectionMethod = "column_name" | "regex_value" | "combined";

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

