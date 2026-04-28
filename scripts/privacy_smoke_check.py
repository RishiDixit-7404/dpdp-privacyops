#!/usr/bin/env python3
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
import sys
from collections.abc import Iterable


REPO_ROOT = Path(__file__).resolve().parents[1]
EXCLUDED_PARTS = {
    ".git",
    ".next",
    ".pytest_cache",
    ".venv",
    "__pycache__",
    "build",
    "dist",
    "node_modules",
}
TEXT_SUFFIXES = {".py", ".sh", ".ts", ".tsx", ".js", ".jsx", ".md", ".mjs", ".cjs", ".json"}
FORBIDDEN_POSITIONING_PHRASES = (
    "certified " + "compliant",
    "legal compliance " + "guaranteed",
    "dpdp " + "approved",
)


@dataclass(frozen=True)
class SmokeFinding:
    path: Path
    line: int
    reason: str
    snippet: str


def main() -> int:
    findings = scan_paths([REPO_ROOT])
    if findings:
        print("Privacy smoke check failed:")
        for finding in findings:
            relative = finding.path.relative_to(REPO_ROOT) if finding.path.is_relative_to(REPO_ROOT) else finding.path
            print(f"  {relative}:{finding.line}: {finding.reason}: {finding.snippet}")
        return 1

    print("Privacy smoke check passed.")
    return 0


def scan_paths(paths: Iterable[Path]) -> list[SmokeFinding]:
    findings: list[SmokeFinding] = []
    for file_path in _iter_files(paths):
        try:
            text = file_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue

        for line_number, line in enumerate(text.splitlines(), start=1):
            findings.extend(_scan_line(file_path, line_number, line))
    return findings


def _iter_files(paths: Iterable[Path]) -> Iterable[Path]:
    for path in paths:
        path = path.resolve()
        if path.is_file():
            if _should_scan(path):
                yield path
            continue
        for file_path in path.rglob("*"):
            if file_path.is_file() and _should_scan(file_path):
                yield file_path


def _should_scan(path: Path) -> bool:
    if path.suffix not in TEXT_SUFFIXES:
        return False
    return not any(part in EXCLUDED_PARTS for part in path.parts)


def _scan_line(path: Path, line_number: int, line: str) -> list[SmokeFinding]:
    stripped = line.strip()
    lowered = stripped.lower()
    findings: list[SmokeFinding] = []

    if _is_frontend_code(path) and re.search(r"\bconsole\.log\s*\(", stripped):
        findings.append(_finding(path, line_number, "console.log is not allowed in frontend code", stripped))

    if _is_frontend_code(path) and not _is_frontend_auth_storage_module(path) and re.search(r"\b(localStorage|sessionStorage)\b", stripped):
        findings.append(_finding(path, line_number, "browser storage is not allowed for privacy payloads", stripped))

    for phrase in FORBIDDEN_POSITIONING_PHRASES:
        if phrase in lowered:
            findings.append(_finding(path, line_number, f"forbidden compliance wording: {phrase}", stripped))

    if path.name == "seed_demo_data.py" and re.search(r"raw_pii_uploaded[\"']?\s*[:=]\s*(true|True)", stripped):
        findings.append(_finding(path, line_number, "demo seed must not set raw_pii_uploaded true", stripped))

    if _is_backend_app_code(path) and re.search(r"\blogging\.(debug|info|warning|error)\s*\(.*(payload|request|body)", stripped):
        findings.append(_finding(path, line_number, "backend logging appears to include request body or payload", stripped))

    return findings


def _finding(path: Path, line_number: int, reason: str, snippet: str) -> SmokeFinding:
    return SmokeFinding(path=path, line=line_number, reason=reason, snippet=snippet[:160])


def _is_frontend_code(path: Path) -> bool:
    return "frontend" in path.parts and path.suffix in {".ts", ".tsx", ".js", ".jsx"}


def _is_frontend_auth_storage_module(path: Path) -> bool:
    return path.name == "auth.ts" and "frontend" in path.parts and "lib" in path.parts


def _is_backend_app_code(path: Path) -> bool:
    parts = path.parts
    return "backend" in parts and "app" in parts and path.suffix == ".py"


if __name__ == "__main__":
    raise SystemExit(main())
