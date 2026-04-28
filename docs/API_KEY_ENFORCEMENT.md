# API Key Enforcement For Consent Writes

Date: 2026-04-27

## Summary

This increment adds project API keys and enforces them on consent event writes.

API key management endpoints now require user authentication and owner/admin project access. This does not add enterprise SSO, billing, or external integrations.

## Files Changed

- `backend/app/models.py`: added `ProjectApiKey`.
- `backend/alembic/versions/20260427_0004_project_api_keys.py`: creates `project_api_keys`.
- `backend/app/services/api_keys.py`: generates, hashes, verifies, and authenticates API keys.
- `backend/app/routers/api_keys.py`: adds project API key management endpoints.
- `backend/app/routers/consent.py`: requires an API key for consent event writes.
- `backend/app/schemas.py`: adds API key request/response schemas.
- `backend/app/main.py`: registers the API key router.
- `backend/app/tests/test_api_keys.py`: covers key management and consent write enforcement.
- `backend/app/tests/test_consent_api.py`: updates consent write tests for API key enforcement.
- `backend/app/tests/test_evidence_report.py`: updates report fixture consent writes.
- `sdk/node/src/client.ts`: requires `apiKey` before consent write calls.
- `sdk/node/tests/client.test.ts`: covers write auth header and missing-key behavior.
- `sdk/node/README.md`: documents SDK API key usage.
- `frontend/lib/api.ts`: adds API key management API calls and sends auth for consent writes.
- `frontend/lib/types.ts`: adds API key types.
- `frontend/components/api-keys/api-key-management.tsx`: adds minimal key list/create/revoke UI.
- `frontend/components/consent/consent-event-form.tsx`: requires a project API key for dashboard consent writes.
- `frontend/app/projects/[projectId]/consent/page.tsx`: adds API key management and session key field.
- `README.md`: documents API key creation and usage.
- `backend/README.md`: documents backend endpoints and consent write enforcement.
- `frontend/README.md`: documents dashboard API key management.
- `docs/RECOVERY_SUMMARY.md`: updated to reflect this increment.
- `docs/AUTH_AND_ACCESS_CONTROL.md`: documents the later user auth and project access-control layer.

## Endpoints Added

- `POST /projects/{project_id}/api-keys`
  - Body: `{ "name": "Production consent writer" }`
  - Returns the raw `api_key` only once, plus safe metadata.
  - Requires owner/admin membership on the project organization.
- `GET /projects/{project_id}/api-keys`
  - Lists key metadata only.
  - Never returns raw keys or `key_hash`.
  - Requires owner/admin membership on the project organization.
- `POST /projects/{project_id}/api-keys/{api_key_id}/revoke`
  - Sets `revoked_at`.
  - Does not delete the key record.
  - Requires owner/admin membership on the project organization.

## Enforcement

Consent writes now require one of these headers:

```text
Authorization: Bearer <api_key>
X-DPDP-API-Key: <api_key>
```

API-key-protected write endpoint:

- `POST /projects/{project_id}/consent-events`

The SDK can also use the project API key for:

- `GET /projects/{project_id}/consent-status`

For consent writes, missing, invalid, revoked, or wrong-project API keys return `401`.

Successful writes update `last_used_at` on the matching API key. Consent ledger and summary admin endpoints now require user bearer auth and project membership.

## Storage Rules

- Raw API keys are generated with Python `secrets`.
- Key format: `dpdp_live_<random_secret>`.
- Raw keys are returned only from the create endpoint.
- Only `key_prefix` and a PBKDF2-SHA256 hash are stored.
- Revoked keys remain stored but cannot authenticate.

## Test Commands And Results

Backend and scanner:

```bash
python -m pytest
```

Result:

```text
131 passed in 27.60s
```

Targeted backend run:

```bash
python -m pytest backend/app/tests/test_api_keys.py backend/app/tests/test_consent_api.py backend/app/tests/test_evidence_report.py
```

Result:

```text
38 passed in 15.23s
```

SDK and frontend checks could not run in this shell because `npm` is not available. Attempted commands:

```bash
cd sdk/node && npm run typecheck
cd sdk/node && npm test
cd frontend && npm run typecheck
cd frontend && npm test
```

```text
npm : The term 'npm' is not recognized as the name of a cmdlet, function, script file, or operable program.
```

## Known Limitations

- This is API-key protection for consent writes, paired with minimal local-MVP user auth for admin/dashboard access.
- Consent write requests use project API keys, not user bearer tokens.
- No key rotation workflow beyond create and revoke.
- No dedicated audit log for API key creation/revocation yet.
