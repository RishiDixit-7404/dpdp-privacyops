from __future__ import annotations

from datetime import datetime
import re

from dpdp_scanner.detectors.base import RegexDetection
from dpdp_scanner.detectors.column_name_detector import identifier_tokens, normalize_identifier


class RegexValueDetector:
    """Deterministic regex detector for sample values."""

    _email_re = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)
    _phone_re = re.compile(r"(?<!\d)(?:\+?91[\s-]?)?[6-9]\d{9}(?!\d)")
    _pan_re = re.compile(r"\b[A-Z]{5}[0-9]{4}[A-Z]\b", re.IGNORECASE)
    _aadhaar_re = re.compile(r"(?<!\d)(?:\d{4}\s\d{4}\s\d{4}|\d{12})(?!\d)")
    _upi_re = re.compile(r"\b[A-Z0-9._-]{2,}@[A-Z][A-Z0-9]{1,30}\b(?!\.)", re.IGNORECASE)
    _bearer_re = re.compile(r"\bBearer\s+[A-Za-z0-9._~+/=-]{8,}\b", re.IGNORECASE)
    _named_secret_re = re.compile(
        r"\b(?:password|passwd|pwd|api[_-]?key|secret|token|access[_-]?token|refresh[_-]?token)"
        r"\s*[:=]\s*[^\s,;]{8,}",
        re.IGNORECASE,
    )
    _key_like_re = re.compile(r"\b(?:sk|pk|rk|api|key|secret|token)[A-Za-z0-9_-]{10,}\b", re.IGNORECASE)
    _date_res = (
        re.compile(r"\b\d{4}-\d{1,2}-\d{1,2}\b"),
        re.compile(r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b"),
        re.compile(r"\b\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)[a-z]*\s+\d{2,4}\b", re.IGNORECASE),
    )
    _date_formats = (
        "%Y-%m-%d",
        "%d/%m/%Y",
        "%d-%m-%Y",
        "%m/%d/%Y",
        "%m-%d-%Y",
        "%d/%m/%y",
        "%d-%m-%y",
        "%d %b %Y",
        "%d %B %Y",
        "%d %b %y",
        "%d %B %y",
    )
    _dob_column_names = {"dob", "date_of_birth", "birth_date", "birthdate", "dateofbirth"}
    _secret_tokens = {"password", "passwd", "pwd", "token", "api", "apikey", "key", "secret", "auth", "bearer"}

    def detect(self, value: object, column_name: str | None = None) -> list[RegexDetection]:
        text = "" if value is None else str(value)
        if not text.strip():
            return []

        detections: list[RegexDetection] = []
        self._append_if_matches(detections, "email", self._email_re.findall(text))
        self._append_if_matches(detections, "indian_phone", [match.group(0) for match in self._phone_re.finditer(text)])
        self._append_if_matches(detections, "pan", [match.group(0) for match in self._pan_re.finditer(text)])
        aadhaar_matches = [
            match.group(0)
            for match in self._aadhaar_re.finditer(text)
            if self._is_plausible_aadhaar_match(match.group(0))
        ]
        self._append_if_matches(detections, "aadhaar", aadhaar_matches)
        self._append_if_matches(detections, "upi_id", [match.group(0) for match in self._upi_re.finditer(text)])

        if self._is_dob_column(column_name):
            dob_matches = self._date_like_matches(text)
            self._append_if_matches(detections, "date_of_birth", dob_matches)

        secret_matches = self._secret_matches(text, column_name)
        self._append_if_matches(detections, "authentication_secret", secret_matches)
        return detections

    @staticmethod
    def _append_if_matches(detections: list[RegexDetection], pii_type: str, matches: list[str]) -> None:
        clean_matches = tuple(match for match in matches if match)
        if clean_matches:
            detections.append(RegexDetection(pii_type=pii_type, matches=clean_matches))

    def _is_dob_column(self, column_name: str | None) -> bool:
        if not column_name:
            return False
        normalized = normalize_identifier(column_name)
        tokens = identifier_tokens(column_name)
        return normalized in self._dob_column_names or "dob" in tokens or ("birth" in tokens and "date" in tokens)

    def _date_like_matches(self, text: str) -> list[str]:
        candidates: list[str] = []
        for pattern in self._date_res:
            candidates.extend(match.group(0) for match in pattern.finditer(text))
        return [candidate for candidate in candidates if self._is_valid_date(candidate)]

    def _is_valid_date(self, value: str) -> bool:
        for date_format in self._date_formats:
            try:
                parsed = datetime.strptime(value, date_format)
            except ValueError:
                continue
            return 1900 <= parsed.year <= datetime.now().year
        return False

    @staticmethod
    def _is_plausible_aadhaar_match(value: str) -> bool:
        digits = re.sub(r"\D", "", value)
        if len(digits) != 12:
            return False

        is_91_prefixed_mobile = digits.startswith("91") and re.fullmatch(r"[6-9]\d{9}", digits[2:])
        return not is_91_prefixed_mobile

    def _secret_matches(self, text: str, column_name: str | None) -> list[str]:
        matches = [match.group(0) for match in self._bearer_re.finditer(text)]
        matches.extend(match.group(0) for match in self._named_secret_re.finditer(text))
        matches.extend(match.group(0) for match in self._key_like_re.finditer(text))

        if self._column_indicates_secret(column_name):
            stripped = text.strip()
            if self._looks_like_secret_value(stripped):
                matches.append(stripped)

        return self._dedupe(matches)

    def _column_indicates_secret(self, column_name: str | None) -> bool:
        if not column_name:
            return False
        tokens = identifier_tokens(column_name)
        normalized = normalize_identifier(column_name)
        return bool(tokens & self._secret_tokens) or normalized in {"api_key", "secret_key", "access_token", "refresh_token"}

    @staticmethod
    def _looks_like_secret_value(value: str) -> bool:
        lowered = value.lower()
        if lowered in {"true", "false", "yes", "no", "none", "null"}:
            return False
        return len(value) >= 8 and bool(re.search(r"[A-Za-z]", value)) and bool(re.search(r"\d|[_\-.=/+]", value))

    @staticmethod
    def _dedupe(values: list[str]) -> list[str]:
        deduped: list[str] = []
        for value in values:
            if value not in deduped:
                deduped.append(value)
        return deduped
