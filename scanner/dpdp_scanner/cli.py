from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console

from dpdp_scanner.detectors.base import ScannerError
from dpdp_scanner.output import write_scan_result
from dpdp_scanner.scanners.csv_scanner import scan_csv as run_csv_scan
from dpdp_scanner.scanners.json_scanner import SUPPORTED_JSON_EXTENSIONS, scan_json as run_json_scan
from dpdp_scanner.scanners.postgres_scanner import scan_postgres_metadata


app = typer.Typer(
    help="Local DPDP PrivacyOps scanner. Raw PII is never printed or uploaded.",
    no_args_is_help=True,
)
console = Console()
error_console = Console(stderr=True)


@app.command("scan-csv")
def scan_csv_command(
    path: Path = typer.Option(..., "--path", help="Path to the CSV file to scan."),
    output: Path = typer.Option(..., "--output", help="Path for the JSON findings output."),
) -> None:
    """Scan a CSV file locally and write masked JSON findings."""
    if not path.is_file():
        error_console.print("Invalid input: CSV path does not exist or is not a file.")
        raise typer.Exit(code=1)

    console.print(f"Scanning CSV locally: {path.name}")
    try:
        result = run_csv_scan(path)
        write_scan_result(result, output)
    except ScannerError as exc:
        error_console.print(f"Scan failed: {exc}")
        raise typer.Exit(code=1) from exc

    console.print(f"Wrote {len(result.findings)} findings to {output}")


@app.command("scan-json")
def scan_json_command(
    path: Path = typer.Option(..., "--path", help="Path to the .json or .jsonl file to scan."),
    output: Path = typer.Option(..., "--output", help="Path for the JSON findings output."),
) -> None:
    """Scan JSON or JSONL locally and write masked JSON findings."""
    if not path.is_file():
        error_console.print("Invalid input: JSON path does not exist or is not a file.")
        raise typer.Exit(code=1)
    if path.suffix.lower() not in SUPPORTED_JSON_EXTENSIONS:
        error_console.print("Invalid input: scan-json supports only .json and .jsonl files.")
        raise typer.Exit(code=1)

    console.print(f"Scanning JSON locally: {path.name}")
    try:
        result = run_json_scan(path)
        write_scan_result(result, output)
    except ScannerError as exc:
        error_console.print(f"Scan failed: {exc}")
        raise typer.Exit(code=1) from exc

    console.print(f"Wrote {len(result.findings)} findings to {output}")


@app.command("scan-postgres")
def scan_postgres_command(
    database_url: str = typer.Option(..., "--database-url", envvar="DATABASE_URL", help="Postgres connection URL."),
    metadata_only: bool = typer.Option(
        True,
        "--metadata-only/--sample-values",
        help="Scanner v0 supports metadata-only Postgres scanning.",
    ),
    output: Path = typer.Option(..., "--output", help="Path for the JSON findings output."),
) -> None:
    """Scan Postgres schema/table/column metadata and write JSON findings."""
    if not metadata_only:
        error_console.print("Invalid input: scanner v0 only supports metadata-only Postgres scanning.")
        raise typer.Exit(code=1)

    console.print("Scanning Postgres metadata locally.")
    try:
        result = scan_postgres_metadata(database_url)
        write_scan_result(result, output)
    except ScannerError as exc:
        error_console.print(f"Scan failed: {exc}")
        raise typer.Exit(code=1) from exc

    console.print(f"Wrote {len(result.findings)} findings to {output}")


if __name__ == "__main__":
    app()
