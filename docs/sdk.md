# Python SDK Reference

Use the telmus Python SDK to embed financial analysis directly into notebooks, scripting workflows, and automated data pipelines.

## Install

```bash
pip install telmus
```

## Import examples

```python
from telmus import TelmusScanner, scan, compare
from telmus.models import ScanResult, HealthResult, ValuationResult, GrowthResult, FlagsResult
```

## When to use the SDK

- You want programmatic access to valuations, health scores, growth metrics, and red-flag indicators.
- You are building a data pipeline, Jupyter notebook, or analytics dashboard.
- You need structured objects that can be inspected, transformed, and exported.

## TelmusScanner class

`TelmusScanner` is the primary programmatic interface for telmus.

### Methods

- `scan(ticker: str) -> ScanResult`
  - Scan a single ticker and return a full structured result.
- `compare(ticker_a: str, ticker_b: str) -> tuple[ScanResult, ScanResult]`
  - Compare two tickers side by side.
- `screen(sector: str | None = None, min_piotroski: int | None = None, max_de: float | None = None) -> list[ScanResult]`
  - Filter the universe by sector, Piotroski score, and leverage.
- `check(ticker: str) -> HealthResult`
  - Run a compact health check for one ticker.
- `serve(port: int = 8080, host: str = "127.0.0.1") -> None`
  - Start the MCP server.
- `info() -> dict`
  - Retrieve server metadata and tool availability.

## ScanResult dataclass

`ScanResult` contains the full result of a scan.

### Fields

- `ticker: str` the stock symbol.
- `valuation: ValuationResult` valuation multiples and comparison metrics.
- `health: HealthResult` balance sheet and earnings health metrics.
- `growth: GrowthResult` revenue and margin momentum metrics.
- `flags: FlagsResult` risk flags and fraud indicators.
- `analyst_brief: str` deterministic summary text.
- `generated_at: str` timestamp when the scan was produced.

## Result models

### ValuationResult

- `pe_ratio: float` price-to-earnings ratio.
- `pb_ratio: float` price-to-book ratio.
- `ev_ebitda: float` enterprise value to EBITDA.
- `sector: str` the company sector.
- `peer_rank: str` valuation ranking relative to peers.

### HealthResult

- `piotroski_f: int` Piotroski F-score, 0 to 9.
- `altman_z: float` Altman Z-score.
- `debt_to_equity: float` debt-to-equity ratio.
- `current_ratio: float` current assets divided by current liabilities.
- `interest_coverage: float` EBIT divided by interest expense.

### GrowthResult

- `revenue_cagr_3y: float` three-year revenue CAGR.
- `pat_cagr_3y: float` three-year PAT CAGR.
- `margin_trend: str` `improving`, `stable`, or `declining`.
- `fcf_yield: float` free cash flow yield.

### FlagsResult

- `beneish_m: float` Beneish M-score.
- `high_de_flag: bool` high leverage warning.
- `negative_fcf_flag: bool` negative free cash flow warning.
- `value_warning: str | None` value concern note.

## Quick examples

### Basic scan

```python
from telmus import scan

result = scan("INFY")
print(result.analyst_brief)
```

### Compare two tickers

```python
from telmus import compare

result_a, result_b = compare("INFY", "TCS")
print(result_a.valuation.pe_ratio, result_b.valuation.pe_ratio)
```

### Loop over a list of tickers

```python
from telmus import scan

tickers = ["INFY", "TCS", "WIPRO"]
for symbol in tickers:
    result = scan(symbol)
    print(symbol, result.health.piotroski_f, result.analyst_brief)
```

### Access specific fields

```python
from telmus import scan

result = scan("INFY")
print("Altman Z:", result.health.altman_z)
print("Revenue CAGR 3y:", result.growth.revenue_cagr_3y)
print("Beneish M:", result.flags.beneish_m)
```

### Convert to pandas DataFrame

```python
import pandas as pd
from telmus import scan

result = scan("INFY")
rows = [{
    "ticker": result.ticker,
    "pe_ratio": result.valuation.pe_ratio,
    "altman_z": result.health.altman_z,
    "revenue_cagr_3y": result.growth.revenue_cagr_3y,
    "beneish_m": result.flags.beneish_m,
}]
df = pd.DataFrame(rows)
print(df)
```

### Export to JSON file

```python
import json
from telmus import scan

result = scan("INFY")
with open("infy_report.json", "w", encoding="utf-8") as f:
    json.dump(result.__dict__, f, indent=2)
```

## Best practices

- Use `scan()` when you need a complete company profile.
- Use `compare()` to evaluate alternatives side by side.
- Use `screen()` to build a shortlist before deeper analysis.
- Use `check()` for fast health validation when you only need risk indicators.
- Use `serve()` to expose the SDK as an MCP tool for AI integrations.

## Integration notes

- The SDK is ideal for notebooks and data pipelines.
- Use structured results to build dashboards, alerts, or export pipelines.
- Always treat `analyst_brief` as a deterministic summary, not investment advice.
