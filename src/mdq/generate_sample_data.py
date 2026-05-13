from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

import pandas as pd


def build_sample_taq(days: int = 5) -> pd.DataFrame:
    """Generate a small multi-day synthetic trade/quote dataset with intentional bad records."""

    rows = []
    base_date = datetime(2026, 5, 11, 13, 30, tzinfo=timezone.utc)
    symbols = ["AAPL", "MSFT"]

    for day in range(days):
        session_start = base_date + timedelta(days=day)

        for symbol_idx, symbol in enumerate(symbols):
            # Small deterministic daily drift so each date has different prices.
            mid = 180.0 + 40.0 * symbol_idx + 0.75 * day

            for i in range(25):
                ts = session_start + timedelta(seconds=i)
                bid = mid + i * 0.01 - 0.01
                ask = mid + i * 0.01 + 0.01

                rows.append(
                    {
                        "event_ts": ts.isoformat(),
                        "symbol": symbol,
                        "event_type": "QUOTE",
                        "exchange": "XNAS",
                        "trade_price": None,
                        "trade_size": None,
                        "bid_price": round(bid, 2),
                        "ask_price": round(ask, 2),
                        "bid_size": 100 + i,
                        "ask_size": 120 + i,
                    }
                )

                if i % 3 == 0:
                    rows.append(
                        {
                            "event_ts": (ts + timedelta(milliseconds=250)).isoformat(),
                            "symbol": symbol,
                            "event_type": "TRADE",
                            "exchange": "XNAS",
                            "trade_price": round((bid + ask) / 2, 2),
                            "trade_size": 50 + i,
                            "bid_price": None,
                            "ask_price": None,
                            "bid_size": None,
                            "ask_size": None,
                        }
                    )

    # Intentional issues to demonstrate the quality report.
    start = base_date
    rows.append(rows[3].copy())  # duplicate event on first date
    rows.append(
        {
            "event_ts": (start + timedelta(days=1, seconds=30)).isoformat(),
            "symbol": "AAPL",
            "event_type": "QUOTE",
            "exchange": "XNAS",
            "trade_price": None,
            "trade_size": None,
            "bid_price": 181.20,
            "ask_price": 181.00,
            "bid_size": 100,
            "ask_size": 100,
        }
    )
    rows.append(
        {
            "event_ts": (start + timedelta(days=1, seconds=31)).isoformat(),
            "symbol": "MSFT",
            "event_type": "TRADE",
            "exchange": "XNAS",
            "trade_price": -10.0,
            "trade_size": 100,
            "bid_price": None,
            "ask_price": None,
            "bid_size": None,
            "ask_size": None,
        }
    )
    rows.append(
        {
            "event_ts": (start + timedelta(days=2, seconds=32)).isoformat(),
            "symbol": "AAPL",
            "event_type": "TRADE",
            "exchange": "XNAS",
            "trade_price": 250.0,
            "trade_size": 100,
            "bid_price": None,
            "ask_price": None,
            "bid_size": None,
            "ask_size": None,
        }
    )

    return pd.DataFrame(rows)


def main() -> None:
    path = Path("data/raw/sample_taq.csv")
    path.parent.mkdir(parents=True, exist_ok=True)
    build_sample_taq(days=5).to_csv(path, index=False)
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
