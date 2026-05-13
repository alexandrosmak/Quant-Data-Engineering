from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import pandas as pd


REQUIRED_COLUMNS = {
    "event_ts",
    "symbol",
    "event_type",
    "exchange",
    "trade_price",
    "trade_size",
    "bid_price",
    "ask_price",
    "bid_size",
    "ask_size",
}


@dataclass(frozen=True)
class QualityIssue:
    """Structured result from a data quality check."""

    check_name: str
    severity: str
    row_count: int
    message: str
    sample_rows: list[dict]


def _sample_rows(df: pd.DataFrame, max_rows: int = 5) -> list[dict]:
    if df.empty:
        return []
    return df.head(max_rows).astype(object).where(pd.notna(df.head(max_rows)), None).to_dict("records")


def check_required_columns(df: pd.DataFrame) -> QualityIssue | None:
    missing = sorted(REQUIRED_COLUMNS.difference(df.columns))
    if not missing:
        return None

    return QualityIssue(
        check_name="required_columns",
        severity="critical",
        row_count=0,
        message=f"Missing required columns: {missing}",
        sample_rows=[],
    )


def check_missing_values(df: pd.DataFrame) -> QualityIssue | None:
    required_for_all_rows = ["event_ts", "symbol", "event_type", "exchange"]
    bad = df[df[required_for_all_rows].isna().any(axis=1)]
    if bad.empty:
        return None

    return QualityIssue(
        check_name="missing_values",
        severity="high",
        row_count=len(bad),
        message="Rows contain missing values in mandatory identifier/timestamp fields.",
        sample_rows=_sample_rows(bad),
    )


def check_duplicate_events(df: pd.DataFrame) -> QualityIssue | None:
    key_cols = ["event_ts", "symbol", "event_type", "exchange", "trade_price", "bid_price", "ask_price"]
    bad = df[df.duplicated(subset=key_cols, keep=False)]
    if bad.empty:
        return None

    return QualityIssue(
        check_name="duplicate_events",
        severity="medium",
        row_count=len(bad),
        message="Duplicate market data events detected.",
        sample_rows=_sample_rows(bad),
    )


def check_non_positive_prices(df: pd.DataFrame) -> QualityIssue | None:
    price_cols = ["trade_price", "bid_price", "ask_price"]
    mask = pd.Series(False, index=df.index)

    for col in price_cols:
        if col in df:
            mask = mask | (df[col].notna() & (df[col] <= 0))

    bad = df[mask]
    if bad.empty:
        return None

    return QualityIssue(
        check_name="non_positive_prices",
        severity="critical",
        row_count=len(bad),
        message="Non-positive prices detected.",
        sample_rows=_sample_rows(bad),
    )


def check_crossed_quotes(df: pd.DataFrame) -> QualityIssue | None:
    quote_rows = df["event_type"].eq("QUOTE")
    bad = df[quote_rows & df["bid_price"].notna() & df["ask_price"].notna() & (df["bid_price"] > df["ask_price"])]
    if bad.empty:
        return None

    return QualityIssue(
        check_name="crossed_quotes",
        severity="high",
        row_count=len(bad),
        message="Quote rows where bid price is greater than ask price.",
        sample_rows=_sample_rows(bad),
    )


def check_timestamp_ordering(df: pd.DataFrame) -> QualityIssue | None:
    sorted_df = df.sort_values(["symbol", "event_ts"], kind="mergesort")
    deltas = sorted_df.groupby("symbol")["event_ts"].diff()
    bad = sorted_df[deltas < pd.Timedelta(0)]
    if bad.empty:
        return None

    return QualityIssue(
        check_name="timestamp_ordering",
        severity="medium",
        row_count=len(bad),
        message="Timestamps move backwards within at least one symbol.",
        sample_rows=_sample_rows(bad),
    )


def check_abnormal_trade_returns(df: pd.DataFrame, max_abs_return_bps: float = 500.0) -> QualityIssue | None:
    trades = df[df["event_type"].eq("TRADE") & df["trade_price"].notna()].copy()
    if trades.empty:
        return None

    trades = trades.sort_values(["symbol", "event_ts"], kind="mergesort")
    trades["prev_trade_price"] = trades.groupby("symbol")["trade_price"].shift(1)
    trades["return_bps"] = 10_000 * (trades["trade_price"] / trades["prev_trade_price"] - 1.0)

    bad = trades[trades["return_bps"].abs() > max_abs_return_bps]
    if bad.empty:
        return None

    return QualityIssue(
        check_name="abnormal_trade_returns",
        severity="medium",
        row_count=len(bad),
        message=f"Trade-to-trade absolute return exceeded {max_abs_return_bps:.0f} bps.",
        sample_rows=_sample_rows(bad),
    )


DEFAULT_CHECKS: list[Callable[[pd.DataFrame], QualityIssue | None]] = [
    check_required_columns,
    check_missing_values,
    check_duplicate_events,
    check_non_positive_prices,
    check_crossed_quotes,
    check_timestamp_ordering,
    check_abnormal_trade_returns,
]


def run_quality_checks(df: pd.DataFrame) -> list[QualityIssue]:
    """Run all checks and return only failed checks."""

    issues: list[QualityIssue] = []
    schema_issue = check_required_columns(df)
    if schema_issue is not None:
        return [schema_issue]

    for check in DEFAULT_CHECKS[1:]:
        issue = check(df)
        if issue is not None:
            issues.append(issue)

    return issues
