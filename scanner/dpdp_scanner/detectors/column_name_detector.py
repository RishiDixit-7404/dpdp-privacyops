from __future__ import annotations

import re
from collections.abc import Iterable

from dpdp_scanner.detectors.base import ColumnNameDetection


STRONG_CONFIDENCE = 0.75
WEAK_CONFIDENCE = 0.55
FREE_TEXT_CONFIDENCE = 0.60


def normalize_identifier(value: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")
    return re.sub(r"_+", "_", normalized)


def identifier_tokens(value: str) -> set[str]:
    normalized = normalize_identifier(value)
    tokens = {token for token in normalized.split("_") if token}
    singular_tokens = {token[:-1] for token in tokens if len(token) > 3 and token.endswith("s")}
    return tokens | singular_tokens


class ColumnNameDetector:
    """Classifies likely PII from schema, table, and column names."""

    _exact_aliases: dict[str, dict[str, str]] = {
        "email": {
            "email": "strong",
            "email_address": "strong",
            "work_email": "strong",
            "personal_email": "strong",
        },
        "indian_phone": {
            "phone": "strong",
            "mobile": "strong",
            "mobile_number": "strong",
            "phone_number": "strong",
            "contact_number": "strong",
            "parent_phone": "strong",
            "guardian_phone": "strong",
            "whatsapp": "strong",
        },
        "pan": {
            "pan": "strong",
            "pan_number": "strong",
            "pan_card": "strong",
        },
        "aadhaar": {
            "aadhaar": "strong",
            "aadhar": "strong",
            "aadhaar_number": "strong",
            "aadhar_number": "strong",
            "aadhaar_no": "strong",
            "aadhar_no": "strong",
        },
        "upi_id": {
            "upi": "strong",
            "upi_id": "strong",
            "vpa": "strong",
            "virtual_payment_address": "strong",
        },
        "date_of_birth": {
            "dob": "strong",
            "date_of_birth": "strong",
            "birth_date": "strong",
            "birthdate": "strong",
            "dateofbirth": "strong",
        },
        "person_name": {
            "name": "strong",
            "full_name": "strong",
            "first_name": "strong",
            "last_name": "strong",
            "student_name": "strong",
            "parent_name": "strong",
            "guardian_name": "strong",
            "customer_name": "strong",
            "patient_name": "strong",
            "employee_name": "strong",
        },
        "address": {
            "address": "strong",
            "street_address": "strong",
            "city": "weak",
            "pincode": "weak",
            "pin_code": "weak",
            "postal_code": "weak",
            "postcode": "weak",
        },
        "student_or_child_data": {
            "student": "strong",
            "student_name": "strong",
            "parent_name": "strong",
            "guardian_name": "strong",
            "class": "weak",
            "grade": "weak",
            "school": "weak",
            "dob": "weak",
        },
        "health_data": {
            "diagnosis": "strong",
            "prescription": "strong",
            "medical_history": "strong",
            "patient": "strong",
            "doctor": "strong",
            "symptoms": "strong",
            "clinical_notes": "strong",
        },
        "employment_data": {
            "resume": "strong",
            "cv": "strong",
            "employee_id": "strong",
            "salary": "strong",
            "designation": "strong",
            "employer": "strong",
            "job_title": "strong",
        },
        "financial_data": {
            "bank_account": "strong",
            "bank_account_number": "strong",
            "ifsc": "strong",
            "card": "strong",
            "card_number": "strong",
            "payment": "strong",
            "invoice": "strong",
            "salary": "strong",
        },
        "authentication_secret": {
            "password": "strong",
            "passwd": "strong",
            "token": "strong",
            "api_key": "strong",
            "apikey": "strong",
            "secret": "strong",
            "secret_key": "strong",
            "auth": "strong",
            "authorization": "strong",
            "bearer": "strong",
            "access_token": "strong",
            "refresh_token": "strong",
        },
        "free_text_possible_pii": {
            "message": "strong",
            "notes": "strong",
            "note": "strong",
            "description": "strong",
            "payload": "strong",
            "prompt": "strong",
            "response": "strong",
            "log": "strong",
            "logs": "strong",
            "metadata": "strong",
            "json": "strong",
            "comment": "strong",
            "comments": "strong",
            "ticket_body": "strong",
            "input_text": "strong",
            "output_text": "strong",
            "request_body": "strong",
            "response_body": "strong",
        },
    }

    _token_rules: dict[str, set[str]] = {
        "email": {"email"},
        "indian_phone": {"phone", "mobile", "contact", "whatsapp"},
        "pan": {"pan"},
        "aadhaar": {"aadhaar", "aadhar"},
        "upi_id": {"upi", "vpa"},
        "date_of_birth": {"dob", "birthdate"},
        "student_or_child_data": {"student", "child", "parent", "guardian", "school", "grade", "class"},
        "health_data": {"diagnosis", "prescription", "medical", "patient", "doctor", "symptom"},
        "employment_data": {"resume", "cv", "employee", "salary", "designation", "employer"},
        "financial_data": {"bank", "ifsc", "card", "payment", "invoice", "salary"},
        "authentication_secret": {"password", "passwd", "token", "api", "apikey", "secret", "auth", "bearer"},
        "free_text_possible_pii": {
            "message",
            "note",
            "notes",
            "description",
            "payload",
            "prompt",
            "response",
            "log",
            "logs",
            "metadata",
            "json",
            "comment",
            "comments",
            "ticket",
            "body",
        },
    }

    def detect(
        self,
        column_name: str,
        context_names: Iterable[str] | None = None,
    ) -> list[ColumnNameDetection]:
        detections: dict[str, ColumnNameDetection] = {}

        for detection in self._detect_identifier(column_name, is_context=False):
            detections[detection.pii_type] = detection

        for context_name in context_names or []:
            for detection in self._detect_identifier(context_name, is_context=True):
                existing = detections.get(detection.pii_type)
                if existing is None or detection.confidence_score > existing.confidence_score:
                    detections[detection.pii_type] = detection

        return list(detections.values())

    def _detect_identifier(self, identifier: str, *, is_context: bool) -> list[ColumnNameDetection]:
        normalized = normalize_identifier(identifier)
        tokens = identifier_tokens(identifier)
        detections: dict[str, ColumnNameDetection] = {}

        for pii_type, aliases in self._exact_aliases.items():
            strength = aliases.get(normalized)
            if strength:
                self._add_detection(detections, pii_type, strength, is_context=is_context)

        for pii_type, rule_tokens in self._token_rules.items():
            if tokens & rule_tokens:
                self._add_detection(detections, pii_type, "strong", is_context=is_context)

        if "birth" in tokens and "date" in tokens:
            self._add_detection(detections, "date_of_birth", "strong", is_context=is_context)

        if "full" in tokens and "name" in tokens:
            self._add_detection(detections, "person_name", "strong", is_context=is_context)

        if "postal" in tokens and "code" in tokens:
            self._add_detection(detections, "address", "weak", is_context=is_context)

        if "api" in tokens and "key" in tokens:
            self._add_detection(detections, "authentication_secret", "strong", is_context=is_context)

        return list(detections.values())

    @staticmethod
    def _add_detection(
        detections: dict[str, ColumnNameDetection],
        pii_type: str,
        strength: str,
        *,
        is_context: bool,
    ) -> None:
        if pii_type == "free_text_possible_pii":
            confidence = FREE_TEXT_CONFIDENCE
            effective_strength = "strong"
        elif is_context:
            confidence = WEAK_CONFIDENCE
            effective_strength = "weak"
        elif strength == "weak":
            confidence = WEAK_CONFIDENCE
            effective_strength = "weak"
        else:
            confidence = STRONG_CONFIDENCE
            effective_strength = "strong"

        existing = detections.get(pii_type)
        if existing is None or confidence > existing.confidence_score:
            detections[pii_type] = ColumnNameDetection(
                pii_type=pii_type,
                confidence_score=confidence,
                strength=effective_strength,
            )
