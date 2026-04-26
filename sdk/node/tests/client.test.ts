import { beforeEach, describe, expect, it, vi } from "vitest";

import { DpdpPrivacyOpsClient, DpdpPrivacyOpsError } from "../src/index.js";

function jsonResponse(body: unknown, init: ResponseInit = {}): Response {
  return new Response(JSON.stringify(body), {
    status: init.status ?? 200,
    headers: { "content-type": "application/json", ...(init.headers ?? {}) }
  });
}

describe("DpdpPrivacyOpsClient", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it("trackConsent sends a granted event", async () => {
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse({ id: "evt_1", status: "granted" }));
    vi.stubGlobal("fetch", fetchMock);
    const client = new DpdpPrivacyOpsClient({ apiBaseUrl: "https://api.example.com", projectId: "project_123" });

    await client.trackConsent({
      externalUserId: "usr_123",
      purpose: "marketing_whatsapp",
      noticeVersion: "v2.1",
      source: "sdk"
    });

    expect(fetchMock).toHaveBeenCalledWith(
      "https://api.example.com/projects/project_123/consent-events",
      expect.objectContaining({ method: "POST" })
    );
    const body = JSON.parse(fetchMock.mock.calls[0][1].body as string) as Record<string, unknown>;
    expect(body.status).toBe("granted");
    expect(body.external_user_id).toBe("usr_123");
    expect(body.notice_version).toBe("v2.1");
  });

  it("withdrawConsent sends a withdrawn event", async () => {
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse({ id: "evt_2", status: "withdrawn" }));
    vi.stubGlobal("fetch", fetchMock);
    const client = new DpdpPrivacyOpsClient({ apiBaseUrl: "https://api.example.com", projectId: "project_123" });

    await client.withdrawConsent({
      externalUserId: "usr_123",
      purpose: "marketing_whatsapp",
      noticeVersion: "v2.1"
    });

    const body = JSON.parse(fetchMock.mock.calls[0][1].body as string) as Record<string, unknown>;
    expect(body.status).toBe("withdrawn");
  });

  it("getConsentStatus calls the correct URL", async () => {
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse({ current_status: "granted" }));
    vi.stubGlobal("fetch", fetchMock);
    const client = new DpdpPrivacyOpsClient({ apiBaseUrl: "https://api.example.com/", projectId: "project_123" });

    await client.getConsentStatus({ externalUserId: "usr_123", purpose: "marketing_whatsapp" });

    expect(fetchMock.mock.calls[0][0]).toBe(
      "https://api.example.com/projects/project_123/consent-status?external_user_id=usr_123&purpose=marketing_whatsapp"
    );
  });

  it("serializes Date occurredAt to ISO", async () => {
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse({ id: "evt_3", status: "granted" }));
    vi.stubGlobal("fetch", fetchMock);
    const client = new DpdpPrivacyOpsClient({ apiBaseUrl: "https://api.example.com", projectId: "project_123" });

    await client.trackConsent({
      externalUserId: "usr_123",
      purpose: "ai_processing",
      noticeVersion: "v1.0",
      occurredAt: new Date("2026-04-26T05:00:00.000Z")
    });

    const body = JSON.parse(fetchMock.mock.calls[0][1].body as string) as Record<string, unknown>;
    expect(body.occurred_at).toBe("2026-04-26T05:00:00.000Z");
  });

  it("throws a typed error on non-2xx without leaking the request payload", async () => {
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse({ detail: "Invalid request" }, { status: 422 }));
    vi.stubGlobal("fetch", fetchMock);
    const client = new DpdpPrivacyOpsClient({ apiBaseUrl: "https://api.example.com", projectId: "project_123" });

    try {
      await client.trackConsent({
        externalUserId: "usr_sensitive",
        purpose: "marketing_whatsapp",
        noticeVersion: "v2.1"
      });
      throw new Error("Expected request to fail");
    } catch (error) {
      expect(error).toBeInstanceOf(DpdpPrivacyOpsError);
      expect((error as DpdpPrivacyOpsError).status).toBe(422);
      expect((error as Error).message).not.toContain("usr_sensitive");
    }
  });
});
