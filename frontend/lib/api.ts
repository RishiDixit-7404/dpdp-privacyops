import type {
  ApiKey,
  ApiKeyCreateResponse,
  AuthMeResponse,
  AuthTokenResponse,
  ConsentEvent,
  ConsentEventCreate,
  ConsentEventFilters,
  ConsentEventListResponse,
  ConsentStatusResponse,
  ConsentSummaryResponse,
  DataRequest,
  DataRequestCreateInput,
  DataRequestDetail,
  DataRequestFilters,
  DataRequestListResponse,
  DataRequestNote,
  DataRequestNoteCreateInput,
  DataRequestUpdateInput,
  EvidenceReportResponse,
  FindingFilters,
  FindingListResponse,
  LoginInput,
  Project,
  ProjectCreateInput,
  PublicDataRequestConfirmation,
  RegisterInput,
  Scan,
  ScanDetail,
  ScannerUploadResponse
} from "@/lib/types";
import { getAccessToken } from "@/lib/auth";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export class ApiError extends Error {
  status: number;
  detail: unknown;

  constructor(status: number, message: string, detail?: unknown) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.detail = detail;
  }
}

function validationMessage(detail: unknown): string {
  if (typeof detail === "string") {
    return detail;
  }
  if (Array.isArray(detail)) {
    return "The request did not match the expected API format.";
  }
  return "The API request failed.";
}

export function apiErrorMessage(error: unknown): string {
  if (error instanceof ApiError) {
    if (error.status === 409) {
      return "This scanner output has already been uploaded.";
    }
    if (error.status === 422) {
      return "The request could not be validated. Check the submitted fields.";
    }
    if (error.status === 404) {
      return error.message || "The requested item was not found.";
    }
    return error.message;
  }
  if (error instanceof Error) {
    return error.message;
  }
  return "Something went wrong while contacting the API.";
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response;
  const token = getAccessToken();
  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      ...init,
      headers: {
        "Content-Type": "application/json",
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
        ...(init?.headers ?? {})
      }
    });
  } catch (error) {
    throw new ApiError(0, "Could not reach the backend API. Is FastAPI running on localhost:8000?", error);
  }

  const contentType = response.headers.get("content-type") ?? "";
  const payload = contentType.includes("application/json") ? await response.json() : null;

  if (!response.ok) {
    const detail = payload && typeof payload === "object" && "detail" in payload ? payload.detail : payload;
    throw new ApiError(response.status, validationMessage(detail), detail);
  }

  return payload as T;
}

function queryString(params: Record<string, string | number | undefined>): string {
  const search = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined && value !== "") {
      search.set(key, String(value));
    }
  }
  const value = search.toString();
  return value ? `?${value}` : "";
}

export function getProjects(): Promise<Project[]> {
  return request<Project[]>("/projects");
}

export function registerUser(input: RegisterInput): Promise<AuthTokenResponse> {
  return request<AuthTokenResponse>("/auth/register", {
    method: "POST",
    body: JSON.stringify(input)
  });
}

export function loginUser(input: LoginInput): Promise<AuthTokenResponse> {
  return request<AuthTokenResponse>("/auth/login", {
    method: "POST",
    body: JSON.stringify(input)
  });
}

export function getCurrentUser(): Promise<AuthMeResponse> {
  return request<AuthMeResponse>("/auth/me");
}

export function createProject(input: ProjectCreateInput): Promise<Project> {
  return request<Project>("/projects", {
    method: "POST",
    body: JSON.stringify(input)
  });
}

export function getProject(projectId: string): Promise<Project> {
  return request<Project>(`/projects/${projectId}`);
}

export function getProjectApiKeys(projectId: string): Promise<ApiKey[]> {
  return request<ApiKey[]>(`/projects/${projectId}/api-keys`);
}

export function createProjectApiKey(projectId: string, name: string): Promise<ApiKeyCreateResponse> {
  return request<ApiKeyCreateResponse>(`/projects/${projectId}/api-keys`, {
    method: "POST",
    body: JSON.stringify({ name })
  });
}

export function revokeProjectApiKey(projectId: string, apiKeyId: string): Promise<ApiKey> {
  return request<ApiKey>(`/projects/${projectId}/api-keys/${apiKeyId}/revoke`, {
    method: "POST"
  });
}

export function getProjectScans(projectId: string): Promise<Scan[]> {
  return request<Scan[]>(`/projects/${projectId}/scans`);
}

export function uploadScannerOutput(projectId: string, payload: unknown): Promise<ScannerUploadResponse> {
  return request<ScannerUploadResponse>(`/projects/${projectId}/scans/upload`, {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export function getProjectFindings(
  projectId: string,
  filters: FindingFilters = {}
): Promise<FindingListResponse> {
  return request<FindingListResponse>(
    `/projects/${projectId}/findings${queryString({
      risk_level: filters.risk_level,
      pii_type: filters.pii_type,
      source_type: filters.source_type,
      scan_id: filters.scan_id,
      limit: filters.limit ?? 100,
      offset: filters.offset ?? 0
    })}`
  );
}

export function getScan(scanId: string): Promise<ScanDetail> {
  return request<ScanDetail>(`/scans/${scanId}`);
}

export function getScanFindings(
  scanId: string,
  filters: Pick<FindingFilters, "limit" | "offset"> = {}
): Promise<FindingListResponse> {
  return request<FindingListResponse>(
    `/scans/${scanId}/findings${queryString({
      limit: filters.limit ?? 100,
      offset: filters.offset ?? 0
    })}`
  );
}

export function createDataRequest(projectId: string, payload: DataRequestCreateInput): Promise<DataRequest> {
  return request<DataRequest>(`/projects/${projectId}/data-requests`, {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export function createPublicDataRequest(
  projectId: string,
  payload: DataRequestCreateInput
): Promise<PublicDataRequestConfirmation> {
  return request<PublicDataRequestConfirmation>(`/public/projects/${projectId}/data-requests`, {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export function getProjectDataRequests(
  projectId: string,
  filters: DataRequestFilters = {}
): Promise<DataRequestListResponse> {
  return request<DataRequestListResponse>(
    `/projects/${projectId}/data-requests${queryString({
      status: filters.status,
      request_type: filters.request_type,
      limit: filters.limit ?? 100,
      offset: filters.offset ?? 0
    })}`
  );
}

export function getDataRequest(requestId: string): Promise<DataRequestDetail> {
  return request<DataRequestDetail>(`/data-requests/${requestId}`);
}

export function updateDataRequest(requestId: string, payload: DataRequestUpdateInput): Promise<DataRequestDetail> {
  return request<DataRequestDetail>(`/data-requests/${requestId}`, {
    method: "PATCH",
    body: JSON.stringify(payload)
  });
}

export function addDataRequestNote(requestId: string, payload: DataRequestNoteCreateInput): Promise<DataRequestNote> {
  return request<DataRequestNote>(`/data-requests/${requestId}/notes`, {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export function createConsentEvent(projectId: string, payload: ConsentEventCreate, apiKey: string): Promise<ConsentEvent> {
  return request<ConsentEvent>(`/projects/${projectId}/consent-events`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${apiKey}`
    },
    body: JSON.stringify(payload)
  });
}

export function getConsentEvents(
  projectId: string,
  filters: ConsentEventFilters = {}
): Promise<ConsentEventListResponse> {
  return request<ConsentEventListResponse>(
    `/projects/${projectId}/consent-events${queryString({
      external_user_id: filters.external_user_id,
      purpose: filters.purpose,
      status: filters.status,
      limit: filters.limit ?? 100,
      offset: filters.offset ?? 0
    })}`
  );
}

export function getConsentStatus(
  projectId: string,
  externalUserId: string,
  purpose: string
): Promise<ConsentStatusResponse> {
  return request<ConsentStatusResponse>(
    `/projects/${projectId}/consent-status${queryString({
      external_user_id: externalUserId,
      purpose
    })}`
  );
}

export function getConsentSummary(projectId: string): Promise<ConsentSummaryResponse> {
  return request<ConsentSummaryResponse>(`/projects/${projectId}/consent-summary`);
}

export function getEvidenceReport(projectId: string): Promise<EvidenceReportResponse> {
  return request<EvidenceReportResponse>(`/projects/${projectId}/evidence-report`);
}
