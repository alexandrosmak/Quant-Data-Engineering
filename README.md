# Market Data Quality Pipeline

The project is intentionally compact: it demonstrates clean ETL structure, data quality checks, test coverage, and researcher-ready outputs.

## Why this project

A quant data engineering platform needs to make new datasets available safely (ETL). This includes extracting raw data from source, cleaning it and standardizing it, before loading it to subsequent analysis (i.e., reporting,  forecasting). That means:

- ingest raw data without destroying the original source
- normalize timestamps, symbols, event types, and numeric fields
- run explicit quality checks before data reaches researchers
- write clean outputs in analysis-friendly formats
- produce a simple report that explains what passed and what failed to ensure proper results communication

## What it does

The pipeline reads a small five-day synthetic TAQ-like CSV containing trades and quotes, validates it, cleans it, and writes:

- `data/processed/market_events.csv`
- `data/processed/market_events.parquet` if `pyarrow` is installed
- `reports/data_quality_report.md`
- `reports/data_quality_summary.json`

Checks implemented:

- required schema validation
- missing-value checks
- duplicate event detection
- non-positive price/size checks
- crossed quote detection where `bid_price > ask_price`
- abnormal trade return check per symbol
- timestamp ordering check per symbol

## Repo structure

```text
market-data-quality-pipeline/
├── data/
│   ├── raw/sample_taq.csv
│   └── processed/market_events.csv
├── notebooks/market_data_quality_demo.ipynb
├── reports/data_quality_report.md
├── src/mdq/
│   ├── pipeline.py
│   ├── quality_checks.py
│   └── generate_sample_data.py
├── tests/test_quality_checks.py
├── pyproject.toml
└── README.md
```

## Notebook demo

Open:

``` notebooks/market_data_quality_demo.ipynb
```

The notebook shows the pipeline step by step: loading raw events, normalizing fields, running checks, inspecting failed checks as a DataFrame, writing outputs, and reading the generated quality report.

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
- The output is written as CSV for easy inspection and Parquet when available for columnar analytics.
- The pipeline exits successfully but flags quality failures in the report, which is useful for research workflows where bad rows may need investigation rather than immediate deletion.


<img width="1864" height="787" alt="image" src="https://github.com/user-attachments/assets/17bff52b-6d96-4e72-ae2c-72655b5ddc94" />

