from __future__ import annotations

from dataclasses import dataclass, field


class ScannerError(Exception):
    """Raised when a scanner cannot complete cleanly."""


@dataclass(frozen=True)
class ColumnNameDetection:
    pii_type: str
    confidence_score: float
    strength: str


@dataclass(frozen=True)
class RegexDetection:
    pii_type: str
    matches: tuple[str, ...] = field(default_factory=tuple)

