# Auth And Project Access Control

Date: 2026-04-27

## Summary

DPDP PrivacyOps now has minimal local-MVP user authentication and project-level access control.

This is not enterprise auth. There is no OAuth, SAML, SSO, password reset, MFA, billing, invite workflow, or hosted identity provider. It is a small foundation so local users can register, log in, own organizations/projects, and restrict project data to organization members.

## Auth Model

- `users`
  - `id`
  - `email`
  - `password_hash`
  - `full_name`
  - `created_at`
  - `disabled_at`
- `organization_memberships`
  - `id`
  - `user_id`
  - `organization_id`
  - `role`
  - `created_at`

Roles:

- `owner`
- `admin`
- `member`

Passwords are stored as PBKDF2-SHA256 hashes with per-password salts. Raw passwords are never stored.

Access tokens are simple HS256 bearer tokens signed by `AUTH_SECRET_KEY`.

## Environment Variables

Backend auth settings:

```bash
AUTH_SECRET_KEY=change-this-local-secret-before-any-shared-use
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

The backend has a development default secret for local MVP convenience. Set a real high-entropy `AUTH_SECRET_KEY` before any shared, hosted, or customer-facing use.

## Auth Endpoints

Register:

```bash
curl -X POST http://127.0.0.1:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "founder@example.com",
    "password": "password-123",
    "full_name": "Founder",
    "organization_name": "Acme Privacy Team"
  }'
```

Login:

```bash
curl -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "founder@example.com",
    "password": "password-123"
  }'
```

Current user:

```bash
curl http://127.0.0.1:8000/auth/me \
  -H "Authorization: Bearer <ACCESS_TOKEN>"
```

Use the returned `access_token` for dashboard/admin APIs:

```bash
curl http://127.0.0.1:8000/projects \
  -H "Authorization: Bearer <ACCESS_TOKEN>"
```

## Project Access Rules

- A user can access only projects in organizations where they have a membership.
- `owner`, `admin`, and `member` can read project data.
- `owner`, `admin`, and `member` can upload scans and view findings.
- `owner`, `admin`, and `member` can use DSR tracking endpoints.
- `owner` and `admin` can create project API keys.
- `owner` and `admin` can revoke project API keys.
- Project create uses the requested organization name:
  - if the user already has owner/admin membership in an organization with that name, the project is created there;
  - if no matching membership exists, a new organization is created and the user becomes owner;
  - if the user is only a member of a matching organization, project creation is denied.

Missing or invalid user bearer auth returns `401`.

Cross-organization project access returns `403`.

## API Key Relationship

Consent event writes remain protected by project API keys:

```text
Authorization: Bearer <PROJECT_API_KEY>
X-DPDP-API-Key: <PROJECT_API_KEY>
```

User bearer tokens protect dashboard/admin APIs. Project API keys protect developer consent write calls, and can also be used by the SDK to read current consent status for a specific external user and purpose.

## Frontend Behavior

The frontend includes:

- `/register`
- `/login`
- logout from the dashboard header
- authenticated dashboard guard for non-public routes
- bearer token attached to backend API calls

The access token is stored in browser `localStorage` under a DPDP PrivacyOps key. The app does not store scanner uploads, privacy request payloads, consent payloads, raw API keys, password hashes, or API key hashes in browser storage.

The raw project API key is still shown only once when created.

## Tests

Backend and scanner:

```bash
python -m pytest
```

Result:

```text
131 passed in 27.60s
```

Privacy smoke check:

```bash
python scripts/privacy_smoke_check.py
```

Result:

```text
Privacy smoke check passed.
```

Frontend and SDK checks could not run in this shell because `npm` is unavailable:

```text
npm : The term 'npm' is not recognized as the name of a cmdlet, function, script file, or operable program.
```

## Known Limitations

- No OAuth, SAML, SSO, MFA, or enterprise identity provider.
- No password reset flow.
- No invitation or role-management UI.
- No account disable UI.
- No refresh tokens.
- Frontend token storage is local-MVP only; production should revisit token storage, rotation, expiry, CSP, and cookie/session strategy.
- Demo user credentials are for local demo only.
