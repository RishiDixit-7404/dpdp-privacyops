# Screenshot Checklist

Use this for pitch decks, AIC/incubator material, and founder demos.

## Local Setup Pre-Check

- Backend running at http://localhost:8000
- Frontend running at http://localhost:3000
- Demo data seeded with `python scripts/seed_demo.py`
- Smoke check passes with `bash scripts/smoke_demo.sh`
- Optional screenshot check passes with `bash scripts/demo_check.sh`

## Browser Size

Use a desktop browser window around 1440 x 900. Keep zoom at 100 percent. Avoid browser sidebars and personal bookmarks.

## No Raw PII Rule

Do not capture raw personal data, live identifiers, secrets, customer production data, or private browser/profile information. Use only seeded masked demo data.

## Screenshots To Capture

| Filename | Screen | What it proves |
| --- | --- | --- |
| `01-dashboard.png` | Home/dashboard or projects | There is a clear product workspace |
| `02-project-detail.png` | Learno AI Tutor project | A scan is tied to a real product/project |
| `03-scan-findings.png` | Findings with high-risk data | The scanner finds risky data locations with masked examples |
| `04-dsr-inbox.png` | User Data Requests | Access, deletion, and grievance workflows can be tracked |
| `05-consent-events.png` | Consent events | Granted/withdrawn consent evidence is available |
| `06-evidence-report.png` | Evidence report | Systems, categories, top risks, readiness, and gaps are summarized |
| `07-readiness-scans.png` | Readiness scans/pricing card | The Rs. 9,999 paid scan workflow is packaged clearly |
| `08-smoke-test.png` | Terminal PASS output | The local demo is reproducible |
| `09-backend-docs.png` | FastAPI docs | The API surface is inspectable |

## Suggested Pitch Deck Order

1. Problem: personal data lives beyond the users table
2. Product workspace
3. Scan findings
4. DSR and consent readiness
5. Evidence report
6. Paid readiness scan package
7. Local smoke test / API docs credibility
