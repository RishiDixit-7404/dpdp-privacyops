from __future__ import annotations

from dpdp_scanner.detectors.column_name_detector import identifier_tokens, normalize_identifier


CRITICAL_TYPES = {"aadhaar", "authentication_secret"}
HIGH_TYPES = {
    "pan",
    "indian_phone",
    "email",
    "upi_id",
    "date_of_birth",
    "student_or_child_data",
    "health_data",
    "financial_data",
}
MEDIUM_TYPES = {"person_name", "address", "employment_data", "free_text_possible_pii"}
CRITICAL_CONTAINER_FIELDS = {
    "log",
    "logs",
    "payload",
    "prompt",
    "response",
    "metadata",
    "json",
    "input_text",
    "output_text",
    "request_body",
    "response_body",
}
FREE_TEXT_CONTAINER_FIELDS = CRITICAL_CONTAINER_FIELDS | {
    "message",
    "notes",
    "description",
    "comment",
    "comments",
    "ticket_body",
}


def risk_level_for(
    pii_type: str,
    field_name: str,
    detection_method: str,
    confidence_score: float,
) -> str:
    is_critical_container = _field_matches_any(field_name, CRITICAL_CONTAINER_FIELDS)

    if detection_method == "column_name" and confidence_score <= 0.55:
        return "low"

    if pii_type in CRITICAL_TYPES:
        return "critical"

    if is_critical_container and pii_type != "free_text_possible_pii":
        return "critical"

    if pii_type in HIGH_TYPES:
        return "high"

    if pii_type in MEDIUM_TYPES:
        return "medium"

    return "low"


def suggested_action_for(pii_type: str, risk_level: str, field_name: str | None = None) -> str:
    if field_name and pii_type != "free_text_possible_pii" and _field_matches_any(field_name, FREE_TEXT_CONTAINER_FIELDS):
        return (
            "Add redaction before log, support-ticket, or prompt ingestion. "
            "Avoid storing personal data in free-text operational systems."
        )
    if pii_type in {"email", "indian_phone"}:
        return (
            "Classify this field as contact data. Ensure purpose limitation, access controls, "
            "retention rules, and deletion workflow coverage."
        )
    if pii_type in {"pan", "aadhaar"}:
        return (
            "Avoid storing this identifier unless strictly required. Encrypt or tokenize it, "
            "restrict access, and add a retention rule."
        )
    if pii_type == "authentication_secret":
        return "Remove secrets from files or logs immediately, rotate exposed credentials, and restrict future access."
    if pii_type == "free_text_possible_pii":
        return "Add redaction before log, support, prompt, or free-text ingestion and define retention controls."
    if pii_type == "student_or_child_data":
        return "Mark this as a high-risk DPDP data flow and review consent, retention, and access controls."
    if pii_type == "health_data":
        return "Classify this as sensitive health-related data and restrict access to approved operational purposes."
    if pii_type == "financial_data":
        return "Classify this as financial data, restrict access, and apply retention and deletion controls."
    if pii_type == "date_of_birth":
        return "Classify this as identity data and verify that collection, retention, and deletion rules are documented."
    if pii_type in {"person_name", "address", "employment_data"}:
        return "Classify this field as personal data and ensure access controls, retention rules, and deletion coverage."
    return f"Review this {risk_level}-risk field and document purpose, access, retention, and deletion controls."


def _field_matches_any(field_name: str, names: set[str]) -> bool:
    normalized_field = normalize_identifier(field_name)
    field_tokens = identifier_tokens(field_name)
    normalized_with_boundaries = f"_{normalized_field}_"
    return any(
        name in field_tokens
        or normalized_field == name
        or f"_{name}_" in normalized_with_boundaries
        for name in names
    )
