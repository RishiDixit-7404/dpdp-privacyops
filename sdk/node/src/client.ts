import type {
  ConsentEventInput,
  ConsentEventResponse,
  ConsentStatus,
  ConsentStatusInput,
  ConsentStatusResponse,
  DpdpPrivacyOpsClientConfig
} from "./types.js";

export class DpdpPrivacyOpsError extends Error {
  status: number;
  detail: unknown;

  constructor(status: number, message: string, detail?: unknown) {
    super(message);
    this.name = "DpdpPrivacyOpsError";
    this.status = status;
    this.detail = detail;
  }
}

export class DpdpPrivacyOpsClient {
  private readonly apiBaseUrl: string;
  private readonly projectId: string;
  private readonly apiKey?: string;

  constructor(config: DpdpPrivacyOpsClientConfig) {
    if (!config.apiBaseUrl) {
      throw new Error("apiBaseUrl is required");
    }
    if (!config.projectId) {
      throw new Error("projectId is required");
    }
    this.apiBaseUrl = config.apiBaseUrl.replace(/\/+$/, "");
    this.projectId = config.projectId;
    this.apiKey = config.apiKey;
  }

  trackConsent(input: ConsentEventInput): Promise<ConsentEventResponse> {
    return this.createConsentEvent(input, "granted");
  }

  withdrawConsent(input: ConsentEventInput): Promise<ConsentEventResponse> {
    return this.createConsentEvent(input, "withdrawn");
  }

  getConsentStatus(input: ConsentStatusInput): Promise<ConsentStatusResponse> {
    const search = new URLSearchParams({
      external_user_id: input.externalUserId,
      purpose: input.purpose
    });
    return this.request<ConsentStatusResponse>(`/projects/${this.projectId}/consent-status?${search.toString()}`);
  }

  private createConsentEvent(input: ConsentEventInput, status: ConsentStatus): Promise<ConsentEventResponse> {
    if (!this.apiKey) {
      throw new Error("apiKey is required to write consent events");
    }
    const occurredAt = input.occurredAt instanceof Date
      ? input.occurredAt.toISOString()
      : input.occurredAt ?? new Date().toISOString();

    return this.request<ConsentEventResponse>(`/projects/${this.projectId}/consent-events`, {
      method: "POST",
      body: JSON.stringify({
        external_user_id: input.externalUserId,
        purpose: input.purpose,
        status,
        notice_version: input.noticeVersion,
        source: input.source ?? null,
        occurred_at: occurredAt,
        metadata: input.metadata ?? null
      })
    });
  }

  private async request<T>(path: string, init?: RequestInit): Promise<T> {
    let response: Response;
    try {
      response = await fetch(`${this.apiBaseUrl}${path}`, {
        ...init,
        headers: {
          "Content-Type": "application/json",
          ...(this.apiKey ? { Authorization: `Bearer ${this.apiKey}` } : {}),
          ...(init?.headers ?? {})
        }
      });
    } catch (error) {
      throw new DpdpPrivacyOpsError(0, "Could not reach the DPDP PrivacyOps API.", error);
    }

    const contentType = response.headers.get("content-type") ?? "";
    const payload = contentType.includes("application/json") ? await response.json() : await response.text();

    if (!response.ok) {
      throw new DpdpPrivacyOpsError(
        response.status,
        `DPDP PrivacyOps API request failed with status ${response.status}.`,
        payload
      );
    }

    return payload as T;
  }
}
