from pathlib import Path

from typer.testing import CliRunner

from dpdp_scanner.cli import app


runner = CliRunner()
FIXTURE_DIR = Path(__file__).parent / "fixtures"


def test_invalid_csv_path_returns_non_zero_and_does_not_create_output(tmp_path: Path) -> None:
    output_path = tmp_path / "findings.json"

    result = runner.invoke(
        app,
        [
            "scan-csv",
            "--path",
            str(tmp_path / "missing.csv"),
            "--output",
            str(output_path),
        ],
    )

    assert result.exit_code != 0
    assert not output_path.exists()


def test_invalid_csv_path_error_does_not_include_raw_sample_values(tmp_path: Path) -> None:
    result = runner.invoke(
        app,
        [
            "scan-csv",
            "--path",
            str(tmp_path / "rahul.sharma@example.com.csv"),
            "--output",
            str(tmp_path / "findings.json"),
        ],
    )

    raw_values = [
        "Rahul Sharma",
        "rahul.sharma@example.com",
        "+91 9876543210",
        "ABCDE1234F",
        "1234 5678 9012",
        "rahul@upi",
        "Bearer abcdefghijk123",
    ]

    assert result.exit_code != 0
    for raw_value in raw_values:
        assert raw_value not in result.output


def test_scan_json_success_writes_output(tmp_path: Path) -> None:
    output_path = tmp_path / "findings.json"

    result = runner.invoke(
        app,
        [
            "scan-json",
            "--path",
            str(FIXTURE_DIR / "sample_logs.jsonl"),
            "--output",
            str(output_path),
        ],
    )

    assert result.exit_code == 0
    assert output_path.exists()
    assert '"scan_type": "json"' in output_path.read_text(encoding="utf-8")


def test_scan_json_rejects_invalid_extension(tmp_path: Path) -> None:
    input_path = tmp_path / "logs.txt"
    output_path = tmp_path / "findings.json"
    input_path.write_text('{"message": "hello"}\n', encoding="utf-8")

    result = runner.invoke(
        app,
        [
            "scan-json",
            "--path",
            str(input_path),
            "--output",
            str(output_path),
        ],
    )

    assert result.exit_code != 0
    assert not output_path.exists()
    assert "supports only .json and .jsonl" in result.output


def test_scan_json_invalid_json_failure_does_not_leak_raw_pii(tmp_path: Path) -> None:
    input_path = tmp_path / "bad.jsonl"
    output_path = tmp_path / "findings.json"
    input_path.write_text('{"message": "rahul.logs@example.com"\n', encoding="utf-8")

    result = runner.invoke(
        app,
        [
            "scan-json",
            "--path",
            str(input_path),
            "--output",
            str(output_path),
        ],
    )

    assert result.exit_code != 0
    assert not output_path.exists()
    assert "Invalid JSONL file at line 1" in result.output
    assert "rahul.logs@example.com" not in result.output
