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
  apiKey: "optional-for-future"
});

await client.trackConsent({
  externalUserId: "student_****",
  purpose: "marketing_whatsapp",
  noticeVersion: "v2.1",
  source: "web_signup",
  metadata: {
    ip_country: "IN",
    ui_surface: "signup_checkbox"
  }
});

await client.withdrawConsent({
  externalUserId: "student_****",
  purpose: "marketing_whatsapp",
  noticeVersion: "v2.1",
  source: "account_settings"
});

const status = await client.getConsentStatus({
  externalUserId: "student_****",
  purpose: "marketing_whatsapp"
});
```

`occurredAt` is optional. If omitted, the SDK sends the current time. A JavaScript `Date` is serialized to an ISO string.

## Privacy Notes

We do not want your raw personal data. The scanner runs inside your environment and sends only metadata, masked examples, confidence scores, and risk tags.

- Use `externalUserId`; do not send email, phone, or name.
- The SDK does not persist data in files, browser storage, or process-level caches.
- The SDK does not add telemetry or analytics.
- Non-2xx errors throw `DpdpPrivacyOpsError` without including the request payload in the error message.

## Current Limitations

- Auth/API key enforcement is not implemented by the backend yet.
- This is not a cookie banner or full preference center.
- Consent summary counts in the API are event counts, not unique-user counts in v0.
