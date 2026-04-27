from __future__ import annotations

import base64
import hashlib
import hmac
import secrets
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models


API_KEY_PREFIX = "dpdp_live_"
DISPLAY_PREFIX_LENGTH = 18
HASH_ITERATIONS = 210_000
SALT_BYTES = 16


def generate_api_key() -> str:
    return f"{API_KEY_PREFIX}{secrets.token_urlsafe(32)}"


def display_prefix(api_key: str) -> str:
    return api_key[:DISPLAY_PREFIX_LENGTH]


def hash_api_key(api_key: str) -> str:
    salt = secrets.token_bytes(SALT_BYTES)
    digest = hashlib.pbkdf2_hmac("sha256", api_key.encode("utf-8"), salt, HASH_ITERATIONS)
    return "pbkdf2_sha256${iterations}${salt}${digest}".format(
        iterations=HASH_ITERATIONS,
        salt=base64.urlsafe_b64encode(salt).decode("ascii"),
        digest=base64.urlsafe_b64encode(digest).decode("ascii"),
    )


def verify_api_key(api_key: str, stored_hash: str) -> bool:
    try:
        algorithm, iterations, salt_value, expected_value = stored_hash.split("$", 3)
        if algorithm != "pbkdf2_sha256":
            return False
        salt = base64.urlsafe_b64decode(salt_value.encode("ascii"))
        expected = base64.urlsafe_b64decode(expected_value.encode("ascii"))
        digest = hashlib.pbkdf2_hmac("sha256", api_key.encode("utf-8"), salt, int(iterations))
    except (ValueError, TypeError):
        return False
    return hmac.compare_digest(digest, expected)


def create_project_api_key(db: Session, project_id: UUID, name: str) -> tuple[models.ProjectApiKey, str]:
    raw_key = generate_api_key()
    api_key = models.ProjectApiKey(
        project_id=project_id,
        name=name.strip(),
        key_prefix=display_prefix(raw_key),
        key_hash=hash_api_key(raw_key),
    )
    db.add(api_key)
    db.commit()
    db.refresh(api_key)
    return api_key, raw_key


def authenticate_project_api_key(db: Session, project_id: UUID, api_key: str) -> models.ProjectApiKey | None:
    key_prefix = display_prefix(api_key)
    statement = (
        select(models.ProjectApiKey)
        .where(
            models.ProjectApiKey.project_id == project_id,
            models.ProjectApiKey.key_prefix == key_prefix,
            models.ProjectApiKey.revoked_at.is_(None),
        )
        .order_by(models.ProjectApiKey.created_at.desc())
    )
    for stored_key in db.scalars(statement):
        if verify_api_key(api_key, stored_key.key_hash):
            stored_key.last_used_at = models.utc_now()
            db.add(stored_key)
            db.flush()
            return stored_key
    return None
