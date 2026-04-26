#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys

from sqlalchemy import select


REPO_ROOT = Path(__file__).resolve().parents[1]
BACKEND_PATH = REPO_ROOT / "backend"
if str(BACKEND_PATH) not in sys.path:
    sys.path.insert(0, str(BACKEND_PATH))

from app import models  # noqa: E402
from app.database import SessionLocal, settings  # noqa: E402


DEMO_ORGANIZATION_NAME = "Acme EdTech Demo"


def main() -> None:
    print(f"Using database: {settings.database_url}")
    with SessionLocal() as db:
        organizations = list(
            db.scalars(select(models.Organization).where(models.Organization.name == DEMO_ORGANIZATION_NAME)).all()
        )
        if not organizations:
            print(f"No demo organization named {DEMO_ORGANIZATION_NAME!r} found. Nothing to delete.")
            return

        project_count = sum(len(organization.projects) for organization in organizations)
        for organization in organizations:
            if organization.name != DEMO_ORGANIZATION_NAME:
                raise RuntimeError("Reset guard refused to delete a non-demo organization.")
            db.delete(organization)
        db.commit()

        print(f"Deleted {len(organizations)} demo organization record(s).")
        print(f"Deleted {project_count} demo project record(s) and related scans, findings, requests, and consent events.")


if __name__ == "__main__":
    main()
