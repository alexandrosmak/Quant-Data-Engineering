# Quant Data Engineering

The current project is a compact market-data ETL and data-quality pipeline. It shows how raw trade/quote-style data can be ingested, normalized, validated, converted into researcher-ready outputs, and inspected through simple analytics.

## Current project: Market Data Quality Pipeline

A quant data engineering platform needs to make new datasets available safely. This means extracting raw data, standardizing it, validating it, and loading clean outputs for downstream research, reporting, and analysis.

This project demonstrates:

- ingesting raw data without destroying the original source
- normalizing timestamps, symbols, event types, and numeric fields
- running explicit data-quality checks before data reaches researchers
- writing outputs in analysis-friendly formats
- producing human-readable and machine-readable quality reports
- creating a filtered research-ready dataset
- computing simple market-data analytics
- generating plots for quick inspection

## ETL workflow

### 1. Extract

The pipeline reads a five-day synthetic TAQ-style CSV containing trades and quotes:

`data/raw/sample_taq.csv`

### 2. Transform

The pipeline normalizes:

- timestamps
- symbols
- event types
- exchange codes
- numeric price and size fields

### 3. Validate

The following data-quality checks are implemented:

- required schema validation
- missing mandatory values
- duplicate event detection
- non-positive price checks
- crossed quote detection where `bid_price > ask_price`
- abnormal trade-return checks per symbol
- timestamp ordering checks per symbol

Quality reports are written to:

`reports/data_quality_report.md`

`reports/data_quality_summary.json`

### 4. Load

Processed outputs are written to:

`data/processed/market_events.csv`

`data/processed/market_events.parquet`

The notebook also creates a filtered research-ready dataset:

`data/processed/valid_market_events.csv`

This removes critical invalid records, such as non-positive trade prices and crossed quotes, before downstream analytics.

## Analytics layer

The notebook adds a small research-facing layer on top of the ETL process.

It computes:

- mid-price
- bid-ask spread
- spread in basis points
- trade-to-trade returns
- daily symbol-level summaries

The summary output is written to:

`reports/research_summary_by_day_symbol.csv`

## Plots

The notebook generates three quick-inspection figures:

- mid-price evolution by symbol
- average bid-ask spread by day
- data-quality issue counts

The figures are saved in:

`reports/figures/`

## Repository structure

```text
Quant-Data-Engineering/
├── data/
│   ├── raw/
│   │   └── sample_taq.csv
│   └── processed/
│       ├── market_events.csv
│       ├── market_events.parquet
│       └── valid_market_events.csv
├── notebooks/
│   └── market_data_quality_demo.ipynb
├── reports/
│   ├── data_quality_report.md
│   ├── data_quality_summary.json
│   ├── research_summary_by_day_symbol.csv
│   └── figures/
│       ├── average_spread_bps.png
│       ├── mid_price_evolution.png
│       └── quality_issue_counts.png
├── src/
│   └── mdq/
│       ├── generate_sample_data.py
│       ├── pipeline.py
│       └── quality_checks.py
├── tests/
│   └── test_quality_checks.py
├── pyproject.toml
└── README.md
```

## Notebook demo

Open:

`notebooks/market_data_quality_demo.ipynb`

The notebook shows the workflow step by step:

```text
raw data
→ normalized events
→ quality checks
→ processed outputs
→ valid research-ready dataset
→ analytics
→ plots
```

## Example output

The included sample data currently produces:

```text
Data Quality Report
Rows processed: 343
Checks failed: 4

Failed checks:
- duplicate_events: 2 rows
- non_positive_prices: 1 row
- crossed_quotes: 1 row
- abnormal_trade_returns: 4 rows
```

## Engineering choices

- The raw input is treated as immutable.
- Validation and transformation are separate functions.
- Each quality check returns structured records, making checks easy to test and extend.
- Outputs are written as CSV for easy inspection and Parquet for columnar analytics.
- The pipeline flags data-quality failures rather than silently dropping them.
- Critical invalid records are removed only in the downstream research-ready dataset.
- The notebook demonstrates how cleaned data can be used immediately for research-style inspection.

## Why this matters

Quant research depends on reliable data. Even simple market-data workflows need explicit validation before data reaches researchers or models.

This project demonstrates the core pattern:

```text
extract raw data
→ transform into normalized events
→ validate quality
→ load processed outputs
→ create research-ready data
→ analyze and visualize
```

The goal is not to build a large production platform, but to show clean structure, testable quality checks, reproducible outputs, and research-oriented data delivery.

## Possible next improvements

Future extensions could include:

- partitioned Parquet output by date and symbol
- DuckDB or ClickHouse loading example
- Airflow or Dagster orchestration
- exchange calendar validation
- point-in-time dataset versioning
- richer monitoring metrics
- larger tick-data simulation
