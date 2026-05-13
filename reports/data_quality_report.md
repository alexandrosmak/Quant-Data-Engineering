# Data Quality Report

Rows processed: 343
Checks failed: 4

## Failed checks

### duplicate_events

- Severity: `medium`
- Rows affected: `2`
- Message: Duplicate market data events detected.

Sample rows:

```json
[
  {
    "event_ts": "2026-05-11 13:30:02+00:00",
    "symbol": "AAPL",
    "event_type": "QUOTE",
    "exchange": "XNAS",
    "trade_price": null,
    "trade_size": null,
    "bid_price": 180.01,
    "ask_price": 180.03,
    "bid_size": 102.0,
    "ask_size": 122.0
  },
  {
    "event_ts": "2026-05-11 13:30:02+00:00",
    "symbol": "AAPL",
    "event_type": "QUOTE",
    "exchange": "XNAS",
    "trade_price": null,
    "trade_size": null,
    "bid_price": 180.01,
    "ask_price": 180.03,
    "bid_size": 102.0,
    "ask_size": 122.0
  }
]
```

### non_positive_prices

- Severity: `critical`
- Rows affected: `1`
- Message: Non-positive prices detected.

Sample rows:

```json
[
  {
    "event_ts": "2026-05-12 13:30:31+00:00",
    "symbol": "MSFT",
    "event_type": "TRADE",
    "exchange": "XNAS",
    "trade_price": -10.0,
    "trade_size": 100.0,
    "bid_price": null,
    "ask_price": null,
    "bid_size": null,
    "ask_size": null
  }
]
```

### crossed_quotes

- Severity: `high`
- Rows affected: `1`
- Message: Quote rows where bid price is greater than ask price.

Sample rows:

```json
[
  {
    "event_ts": "2026-05-12 13:30:30+00:00",
    "symbol": "AAPL",
    "event_type": "QUOTE",
    "exchange": "XNAS",
    "trade_price": null,
    "trade_size": null,
    "bid_price": 181.2,
    "ask_price": 181.0,
    "bid_size": 100.0,
    "ask_size": 100.0
  }
]
```

### abnormal_trade_returns

- Severity: `medium`
- Rows affected: `4`
- Message: Trade-to-trade absolute return exceeded 500 bps.

Sample rows:

```json
[
  {
    "event_ts": "2026-05-13 13:30:32+00:00",
    "symbol": "AAPL",
    "event_type": "TRADE",
    "exchange": "XNAS",
    "trade_price": 250.0,
    "trade_size": 100.0,
    "bid_price": null,
    "ask_price": null,
    "bid_size": null,
    "ask_size": null,
    "prev_trade_price": 181.74,
    "return_bps": 3755.9150434686917
  },
  {
    "event_ts": "2026-05-14 13:30:00.250000+00:00",
    "symbol": "AAPL",
    "event_type": "TRADE",
    "exchange": "XNAS",
    "trade_price": 182.25,
    "trade_size": 50.0,
    "bid_price": null,
    "ask_price": null,
    "bid_size": null,
    "ask_size": null,
    "prev_trade_price": 250.0,
    "return_bps": -2710.0
  },
  {
    "event_ts": "2026-05-12 13:30:31+00:00",
    "symbol": "MSFT",
    "event_type": "TRADE",
    "exchange": "XNAS",
    "trade_price": -10.0,
    "trade_size": 100.0,
    "bid_price": null,
    "ask_price": null,
    "bid_size": null,
    "ask_size": null,
    "prev_trade_price": 220.99,
    "return_bps": -10452.509163310557
  },
  {
    "event_ts": "2026-05-13 13:30:00.250000+00:00",
    "symbol": "MSFT",
    "event_type": "TRADE",
    "exchange": "XNAS",
    "trade_price": 221.5,
    "trade_size": 50.0,
    "bid_price": null,
    "ask_price": null,
    "bid_size": null,
    "ask_size": null,
    "prev_trade_price": -10.0,
    "return_bps": -231500.0
  }
]
```
