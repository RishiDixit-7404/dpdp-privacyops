# 3-Minute MVP Demo Script

## Opening Line

DPDP PrivacyOps helps Indian SaaS, edtech, healthtech, HRtech, and AI teams find personal data, see risk, and produce technical evidence without moving raw personal data out of their environment.

## Problem Statement

Rahul, as a CTO or founder, the hard part is not writing one privacy policy. The hard part is knowing where personal data actually lives: databases, CSV exports, support tickets, logs, AI prompts, and payment payloads. When a user asks for access, correction, deletion, or consent withdrawal, the team needs a reliable workflow and evidence trail.

## Run Local Scanner / Upload Scanner JSON

Log in with the seeded demo account first:

- email: `demo.admin@example.test`
- password: `demo-password-123`

Start with the local scanner. It runs inside the customer environment and scans CSV, Postgres metadata, JSON, and JSONL files.

Use this positioning exactly:

> We do not want your raw personal data. The scanner runs inside your environment and sends only metadata, masked examples, counts, confidence scores, and risk tags.

Open the project page and upload the scanner JSON. Point out that the dashboard shows only scan metadata and masked examples.

## Show Findings Inventory

Open the findings inventory. Show filters by risk level, PII type, source type, and scan. Explain that this becomes the first data map: where personal data exists, what type it is, and why it matters.

## Show High-Risk Logs/Prompts Examples

Filter for critical or high risk JSON findings. Show examples such as Aadhaar-like identifiers in support tickets, phone numbers in AI tutor prompts, and secrets in request bodies. Emphasize that these are masked examples and remediation is plain-language.

## Show DSR Inbox

Open User Data Requests. Show access, deletion, grievance, and correction requests. Open one request detail and show notes plus the audit timeline. Explain that v0 tracks workflow and evidence; it does not automatically delete data across customer systems.

## Show Consent Events

Open Consent Events. Show the append-only ledger of granted and withdrawn consent events by external user ID and purpose. Show that owners/admins can create a project API key for consent writes, and that the raw key is displayed only once. Check current status for a purpose such as `marketing_whatsapp`. Mention that the Node SDK lets developers record consent events from their product using the project API key.

## Show Evidence Report

Open Evidence Report. Walk through the executive summary, scan inventory, risk summary, top risks, DSR workflow status, consent event ledger, recommended remediation, and readiness gaps.

Use the disclaimer: this is a technical evidence report for DPDP readiness. It is not a legal compliance certificate.

Show browser print-to-PDF as the v0 export workflow.

## Closing Line

This MVP gives a founder or CTO a practical path from unknown data exposure to a working data map, request workflow, consent ledger, and DPDP readiness evidence without asking them to upload raw personal data.
