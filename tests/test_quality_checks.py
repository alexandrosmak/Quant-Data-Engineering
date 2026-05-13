from __future__ import annotations

import pandas as pd

from mdq.pipeline import normalize_market_data
from mdq.quality_checks import (
    check_crossed_quotes,
    check_duplicate_events,
    check_non_positive_prices,
    run_quality_checks,
)


def test_crossed_quote_is_detected() -> None:
    df = pd.DataFrame(
        [
            {
                "event_ts": "2026-05-12T13:30:00Z",
                "symbol": "AAPL",
                "event_type": "QUOTE",
                "exchange": "XNAS",
                "trade_price": None,
                "trade_size": None,
                "bid_price": 101.0,
                "ask_price": 100.0,
                "bid_size": 100,
                "ask_size": 100,
            }
        ]
    )
    normalized = normalize_market_data(df)
    issue = check_crossed_quotes(normalized)

    assert issue is not None
    assert issue.check_name == "crossed_quotes"
    assert issue.row_count == 1


def test_non_positive_price_is_detected() -> None:
    df = pd.DataFrame(
        [
            {
                "event_ts": "2026-05-12T13:30:00Z",
                "symbol": "MSFT",
                "event_type": "TRADE",
                "exchange": "XNAS",
                "trade_price": 0.0,
                "trade_size": 10,
                "bid_price": None,
                "ask_price": None,
                "bid_size": None,
                "ask_size": None,
            }
        ]
    )
    normalized = normalize_market_data(df)
    issue = check_non_positive_prices(normalized)

    assert issue is not None
    assert issue.check_name == "non_positive_prices"


def test_duplicate_event_is_detected() -> None:
    row = {
        "event_ts": "2026-05-12T13:30:00Z",
        "symbol": "AAPL",
        "event_type": "TRADE",
        "exchange": "XNAS",
        "trade_price": 180.0,
        "trade_size": 10,
        "bid_price": None,
        "ask_price": None,
        "bid_size": None,
        "ask_size": None,
    }
    normalized = normalize_market_data(pd.DataFrame([row, row]))
    issue = check_duplicate_events(normalized)

    assert issue is not None
    assert issue.row_count == 2


def test_clean_dataset_has_no_issues() -> None:
    df = pd.DataFrame(
        [
            {
                "event_ts": "2026-05-12T13:30:00Z",
                "symbol": "AAPL",
                "event_type": "QUOTE",
                "exchange": "XNAS",
                "trade_price": None,
                "trade_size": None,
                "bid_price": 99.0,
                "ask_price": 100.0,
                "bid_size": 100,
                "ask_size": 100,
            },
            {
                "event_ts": "2026-05-12T13:30:01Z",
                "symbol": "AAPL",
                "event_type": "TRADE",
                "exchange": "XNAS",
                "trade_price": 99.5,
                "trade_size": 10,
                "bid_price": None,
                "ask_price": None,
                "bid_size": None,
                "ask_size": None,
            },
        ]
    )
    normalized = normalize_market_data(df)
    issues = run_quality_checks(normalized)

    assert issues == []
