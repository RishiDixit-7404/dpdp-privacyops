export type ConsentStatus = "granted" | "withdrawn";

export interface DpdpPrivacyOpsClientConfig {
  apiBaseUrl: string;
  projectId: string;
  apiKey?: string;
}

export interface ConsentEventInput {
  externalUserId: string;
  purpose: string;
  noticeVersion: string;
  source?: string;
  occurredAt?: string | Date;
  metadata?: Record<string, unknown>;
}

export interface ConsentStatusInput {
  externalUserId: string;
  purpose: string;
}

export interface ConsentEventResponse {
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
