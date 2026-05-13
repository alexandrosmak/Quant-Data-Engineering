from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

import pandas as pd

from mdq.quality_checks import QualityIssue, run_quality_checks


NUMERIC_COLUMNS = [
    "trade_price",
    "trade_size",
    "bid_price",
    "ask_price",
    "bid_size",
    "ask_size",
]


def load_raw_market_data(path: Path) -> pd.DataFrame:
    """Load raw market data from CSV without mutating source file."""

    df = pd.read_csv(path)
    return df


def normalize_market_data(df: pd.DataFrame) -> pd.DataFrame:
    """Apply lightweight normalization used before quality checks."""

    out = df.copy()
    out.columns = [col.strip().lower() for col in out.columns]

    out["event_ts"] = pd.to_datetime(out["event_ts"], utc=True, errors="coerce", format="mixed")
    out["symbol"] = out["symbol"].astype("string").str.upper().str.strip()
    out["event_type"] = out["event_type"].astype("string").str.upper().str.strip()
    out["exchange"] = out["exchange"].astype("string").str.upper().str.strip()

    for col in NUMERIC_COLUMNS:
        out[col] = pd.to_numeric(out[col], errors="coerce")

    return out


def clean_for_research(df: pd.DataFrame) -> pd.DataFrame:
    """Create a ready dataset while preserving all valid event types."""

    out = df.copy()
    out = out.drop_duplicates()
    out = out.sort_values(["symbol", "event_ts"], kind="mergesort").reset_index(drop=True)
    out["event_date"] = out["event_ts"].dt.date.astype("string")
    return out


def write_outputs(clean_df: pd.DataFrame, issues: list[QualityIssue], output_dir: Path, report_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)

    clean_df.to_csv(output_dir / "market_events.csv", index=False)

    try:
        clean_df.to_parquet(output_dir / "market_events.parquet", index=False)
    except ImportError:
        # Parquet might be preferred for analytics, but CSV keeps the demo runnable with only pandas.
        pass

    summary = {
        "rows_processed": int(len(clean_df)),
        "checks_failed": len(issues),
        "issues": [asdict(issue) for issue in issues],
    }

    (report_dir / "data_quality_summary.json").write_text(json.dumps(summary, indent=2, default=str), encoding="utf-8")
    (report_dir / "data_quality_report.md").write_text(render_markdown_report(summary), encoding="utf-8")


def render_markdown_report(summary: dict) -> str:
    lines = [
        "# Data Quality Report",
        "",
        f"Rows processed: {summary['rows_processed']}",
        f"Checks failed: {summary['checks_failed']}",
        "",
    ]

    if not summary["issues"]:
        lines.append("All checks passed.")
        return "\n".join(lines) + "\n"

    lines.append("## Failed checks")
    lines.append("")

    for issue in summary["issues"]:
        lines.extend(
            [
                f"### {issue['check_name']}",
                "",
                f"- Severity: `{issue['severity']}`",
                f"- Rows affected: `{issue['row_count']}`",
                f"- Message: {issue['message']}",
                "",
            ]
        )

        if issue["sample_rows"]:
            lines.append("Sample rows:")
            lines.append("")
            lines.append("```json")
            lines.append(json.dumps(issue["sample_rows"], indent=2, default=str))
            lines.append("```")
            lines.append("")

    return "\n".join(lines)


def run_pipeline(input_path: Path, output_dir: Path, report_dir: Path) -> list[QualityIssue]:
    raw = load_raw_market_data(input_path)
    normalized = normalize_market_data(raw)
    issues = run_quality_checks(normalized)
    clean = clean_for_research(normalized)
    write_outputs(clean, issues, output_dir, report_dir)
    return issues


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run market data quality pipeline.")
    parser.add_argument("--input", type=Path, default=Path("data/raw/sample_taq.csv"))
    parser.add_argument("--output-dir", type=Path, default=Path("data/processed"))
    parser.add_argument("--report-dir", type=Path, default=Path("reports"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    issues = run_pipeline(args.input, args.output_dir, args.report_dir)
    print(f"Pipeline complete. Failed checks: {len(issues)}")
    for issue in issues:
        print(f"- {issue.check_name}: {issue.row_count} rows affected")


if __name__ == "__main__":
    main()
