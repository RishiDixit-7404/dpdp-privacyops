# DPDP PrivacyOps Node SDK

TypeScript SDK for the DPDP PrivacyOps Consent Event API v0.

This SDK records append-only consent events and reads current consent status by `external_user_id` and purpose. It does not collect telemetry, does not store data locally, and does not log request payloads.

## Install

```bash
npm install @dpdp-privacyops/node
```

For local development in this repository:

```bash
cd sdk/node
npm install --no-audit --no-fund
npm run typecheck
npm test
npm run build
```

## Usage

```ts
import { DpdpPrivacyOpsClient } from "@dpdp-privacyops/node";

const client = new DpdpPrivacyOpsClient({
  apiBaseUrl: "http://localhost:8000",
  projectId: "project-uuid",
  apiKey: "dpdp_live_..."
});

await client.trackConsent({
  externalUserId: "usr_123",
  purpose: "marketing_whatsapp",
  noticeVersion: "v2.1",
  source: "web_signup",
  metadata: {
    ip_country: "IN",
    ui_surface: "signup_checkbox"
  }
});

await client.withdrawConsent({
  externalUserId: "usr_123",
  purpose: "marketing_whatsapp",
  noticeVersion: "v2.1",
  source: "account_settings"
});

const status = await client.getConsentStatus({
  externalUserId: "usr_123",
  purpose: "marketing_whatsapp"
});
```

`occurredAt` is optional. If omitted, the SDK sends the current time. A JavaScript `Date` is serialized to an ISO string.

`apiKey` is required for write calls that create consent events, including `trackConsent` and `withdrawConsent`. The SDK sends it as:

```text
Authorization: Bearer <apiKey>
```

Read calls such as `getConsentStatus` can still be used without `apiKey` in the local MVP.

## Privacy Notes

- Use `externalUserId`; do not send email, phone, or name.
- The SDK does not persist data in files, browser storage, or process-level caches.
- The SDK does not add telemetry or analytics.
- Non-2xx errors throw `DpdpPrivacyOpsError` without including the request payload in the error message.

## Current Limitations

- Backend API key enforcement protects consent event writes, but this is not full user login/auth.
- This is not a cookie banner or full preference center.
- Consent summary counts in the API are event counts, not unique-user counts in v0.
- The SDK is included in the local MVP demo, but production use still requires hosted deployment hardening and full auth around admin workflows.
