import type {
  FindingFilters,
  FindingListResponse,
  Project,
  ProjectCreateInput,
  Scan,
  ScanDetail,
  ScannerUploadResponse
} from "@/lib/types";

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
      return "The scanner output could not be validated. Check that it is unmodified scanner JSON.";
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
  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      ...init,
      headers: {
        "Content-Type": "application/json",
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

export function createProject(input: ProjectCreateInput): Promise<Project> {
  return request<Project>("/projects", {
    method: "POST",
    body: JSON.stringify(input)
  });
}

export function getProject(projectId: string): Promise<Project> {
  return request<Project>(`/projects/${projectId}`);
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

