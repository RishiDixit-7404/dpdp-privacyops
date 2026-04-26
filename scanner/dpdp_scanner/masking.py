from __future__ import annotations

import re


def mask_value(value: object, pii_type: str) -> str:
    text = "" if value is None else str(value)
    if not text:
        return ""

    if pii_type == "email":
        return _mask_email(text)
    if pii_type == "indian_phone":
        return _mask_indian_phone(text)
    if pii_type == "pan":
        return _mask_pan(text)
    if pii_type == "aadhaar":
        return _mask_aadhaar(text)
    if pii_type == "upi_id":
        return _mask_upi(text)
    if pii_type == "authentication_secret":
        return _mask_secret(text)
    if pii_type == "free_text_possible_pii":
        return "[masked free text]"
    return generic_mask(text)


def generic_mask(value: object) -> str:
    text = "" if value is None else str(value)
    if not text:
        return ""
    if len(text) <= 4:
        return "*" * len(text)
    return f"{text[:2]}{'*' * (len(text) - 4)}{text[-2:]}"


def _mask_email(value: str) -> str:
    if "@" not in value:
        return generic_mask(value)
    local, domain = value.split("@", 1)
    if not local:
        return f"*@{domain}"
    return f"{local[0]}{'*' * max(len(local) - 1, 1)}@{domain}"


def _mask_indian_phone(value: str) -> str:
    match = re.search(r"(?P<prefix>\+?91[\s-]?)?(?P<number>[6-9]\d{9})", value)
    if not match:
        return generic_mask(value)
    prefix = match.group("prefix") or ""
    number = match.group("number")
    return f"{prefix}{number[:2]}******{number[-2:]}"


def _mask_pan(value: str) -> str:
    cleaned = value.strip().upper()
    if len(cleaned) < 3:
        return generic_mask(value)
    return f"{cleaned[:3]}********"


def _mask_aadhaar(value: str) -> str:
    digits = re.sub(r"\D", "", value)
    if len(digits) < 4:
        return generic_mask(value)
    return f"**** **** {digits[-4:]}"


def _mask_upi(value: str) -> str:
    if "@" not in value:
        return generic_mask(value)
    local, handle = value.split("@", 1)
    if not local:
        return f"*@{handle}"
    return f"{local[0]}{'*' * max(len(local) - 1, 4)}@{handle}"


def _mask_secret(value: str) -> str:
    bearer_match = re.match(r"(?P<prefix>Bearer\s+)(?P<secret>.+)", value, re.IGNORECASE)
    if bearer_match:
        secret = bearer_match.group("secret")
        return f"{bearer_match.group('prefix')}{secret[:2]}********"

    assignment_match = re.match(r"(?P<prefix>[^:=]{2,40}\s*[:=]\s*)(?P<secret>.+)", value)
    if assignment_match:
        secret = assignment_match.group("secret")
        return f"{assignment_match.group('prefix')}{secret[:2]}********"

    stripped = value.strip()
    if len(stripped) <= 2:
        return "*" * len(stripped)
    return f"{stripped[:2]}********"

