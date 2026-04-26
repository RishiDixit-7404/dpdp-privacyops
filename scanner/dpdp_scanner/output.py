from __future__ import annotations

import json
from pathlib import Path

from dpdp_scanner.models import ScanResult


def write_scan_result(result: ScanResult, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = result.model_dump(mode="json")
    output_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

