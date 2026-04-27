# API Key Enforcement For Consent Writes

Date: 2026-04-27

## Summary

This increment adds project API keys and enforces them on consent event writes.

It does not add full user login, sessions, billing, external integrations, or broader project access control. The API key management endpoints are local-MVP admin endpoints until full user auth is added.

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

## Endpoints Added

- `POST /projects/{project_id}/api-keys`
  - Body: `{ "name": "Production consent writer" }`
  - Returns the raw `api_key` only once, plus safe metadata.
- `GET /projects/{project_id}/api-keys`
  - Lists key metadata only.
  - Never returns raw keys or `key_hash`.
- `POST /projects/{project_id}/api-keys/{api_key_id}/revoke`
  - Sets `revoked_at`.
  - Does not delete the key record.

## Enforcement

Consent writes now require one of these headers:

```text
Authorization: Bearer <api_key>
X-DPDP-API-Key: <api_key>
```

Protected endpoint:

- `POST /projects/{project_id}/consent-events`

Unauthenticated, invalid, revoked, or wrong-project keys return `401`.

Successful writes update `last_used_at` on the matching API key. Consent read endpoints remain unauthenticated for the local MVP.

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
120 passed in 37.79s
```

Targeted backend run:

```bash
python -m pytest backend/app/tests/test_api_keys.py backend/app/tests/test_consent_api.py backend/app/tests/test_evidence_report.py
```

Result:

```text
37 passed in 29.87s
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

- This is API-key protection for consent writes, not full user login/auth.
- API key management endpoints are unauthenticated local-MVP admin endpoints until login and project access control exist.
- Consent read endpoints remain unauthenticated.
- No key rotation workflow beyond create and revoke.
- No dedicated audit log for API key creation/revocation yet.
