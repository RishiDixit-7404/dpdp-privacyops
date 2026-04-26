from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
from types import ModuleType


REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPTS_DIR = REPO_ROOT / "scripts"


def _load_script(name: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, SCRIPTS_DIR / f"{name}.py")
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def test_demo_seed_uses_guarded_demo_identity() -> None:
    seed_demo_data = _load_script("seed_demo_data")

    assert seed_demo_data.DEMO_ORGANIZATION_NAME == "Acme EdTech Demo"
    assert seed_demo_data.DEMO_PROJECT_NAME == "Student Learning Platform"
    assert seed_demo_data.DEMO_FINDINGS
    assert all(item["masked_examples"] for item in seed_demo_data.DEMO_FINDINGS)


def test_reset_script_deletes_only_named_demo_organization() -> None:
    reset_demo_data = _load_script("reset_demo_data")

    assert reset_demo_data.DEMO_ORGANIZATION_NAME == "Acme EdTech Demo"


def test_privacy_smoke_check_detects_frontend_console_log(tmp_path: Path) -> None:
    privacy_smoke_check = _load_script("privacy_smoke_check")
    frontend_dir = tmp_path / "frontend"
    frontend_dir.mkdir()
    unsafe_file = frontend_dir / "upload.tsx"
    unsafe_file.write_text("console.log(uploadedScannerJson)\n", encoding="utf-8")

    findings = privacy_smoke_check.scan_paths([tmp_path])

    assert any("console.log" in finding.reason for finding in findings)


def test_privacy_smoke_check_detects_forbidden_positioning(tmp_path: Path) -> None:
    privacy_smoke_check = _load_script("privacy_smoke_check")
    doc = tmp_path / "README.md"
    forbidden = "certified " + "compliant"
    doc.write_text(f"This product is {forbidden}.\n", encoding="utf-8")

    findings = privacy_smoke_check.scan_paths([tmp_path])

    assert any(forbidden in finding.reason for finding in findings)
