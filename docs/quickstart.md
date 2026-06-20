# Quickstart

This quickstart guide walks you through installing telmus, scanning your first stock, understanding every field in the output, exporting JSON, and comparing two tickers.

## 1. Install

telmus requires Python 3.9 or newer.

```bash
pip install telmus
```

If you use a virtual environment, activate it before installing.

## 2. Scan your first stock

Run the first scan for Infosys:

```bash
telmus scan INFY
```

Expected output example:

```text
Valuation
---------
Ticker    P/E    P/B    EV/EBITDA
INFY      12.92  2.8    8.11

Health
------
Ticker    Piotroski F    Altman Z    D/E    Current Ratio    Interest Coverage
INFY      4              3.12        0.29   1.9              87.0

Growth
------
Ticker    Revenue CAGR 3y    Margin Trend
INFY      3.4%                stable

Analyst brief
------------
Weak fundamentals (Piotroski F of 4). Revenue growth 3.4% over three years, margins stable. No red flags detected. Suitable for DCF or comparable company analysis.
```

The output includes three tables:

- `Valuation` for the market multiple view.
- `Health` for balance sheet and earnings quality.
- `Growth` for revenue and margin momentum.
- A deterministic `Analyst brief` panel summarizing the result.

## 3. Understand the output

### P/E ratio
The price-to-earnings ratio compares a company's market price to its earnings per share. A lower P/E can indicate value or earnings risk; a higher P/E can indicate strong growth expectations or an expensive stock.

### P/B ratio
Price-to-book compares the stock price to the company's book value per share. Values below 1.0 may signal that the market values the company below its accounting assets, while values above 3.0 suggest investors are paying a premium for intangible assets or future growth.

### EV/EBITDA
Enterprise value divided by EBITDA measures how expensive the company is relative to its operating cash profit. Lower EV/EBITDA is generally more attractive, while values above 15-20 can indicate a richly valued company.

### Piotroski F-score
The Piotroski F-score is a nine-point score that measures financial strength.

- `0-2`: distressed
- `3-4`: weak
- `5-6`: adequate
- `7-9`: strong

A higher score means stronger profitability, cash flow, leverage, liquidity, and earnings quality.

### Altman Z-score
The Altman Z-score estimates bankruptcy risk using five balance-sheet and income-statement factors.

- `Z > 2.99`: safe zone
- `1.81 <= Z <= 2.99`: grey zone
- `Z < 1.81`: distress zone

### Beneish M-score
The Beneish M-score estimates the likelihood of earnings manipulation.

- `M <= -2.22`: normal range
- `M > -2.22`: manipulation risk is elevated

A higher score is a warning sign for aggressive accounting or earnings management.

### Revenue CAGR
Revenue compound annual growth rate measures how quickly sales have grown over three years. A positive CAGR means the business is expanding revenue; a negative CAGR means revenue is contracting.

### Margin trend
Margin trend describes how profitability is moving over time:

- `improving` margins are expanding.
- `stable` margins are holding steady.
- `declining` margins are contracting.

## 4. Export to JSON

Use `--json` to print structured output and `--export` to save a report file.

```bash
telmus scan INFY --json
```

```bash
telmus scan INFY --export report.json
```

The generated JSON contains `valuation`, `health`, `growth`, `flags`, and `analyst_brief` sections, making it easy to load into analytics pipelines.

## 5. Compare two stocks

Compare INFY with TCS:

```bash
telmus compare INFY TCS
```

Expected comparison output:

```text
Ticker    P/E    P/B    EV/EBITDA    Piotroski F    Altman Z    Revenue CAGR 3y    Margin Trend
INFY      12.92  2.8    8.11         4              3.12        3.4%                stable
TCS       25.40  5.1    15.2         7              4.50        7.8%                improving

Analyst brief
------------
INFY: stable revenue growth with a moderate balance sheet. TCS: stronger earnings quality and growth, but a higher valuation multiple.
```

## 6. What gets auto-generated

Every main command in `telmus` generates high-quality files and opens interactive dashboards in your default web browser instantly.

### When running `telmus scan TICKER`:
1. **`{TICKER}_analysis.xlsx` (Excel Workbook, ~15 KB)**:
   - **Dashboard (Sheet 1, Index 0)**: The active home tab featuring a summary data table and three grid-aligned charts (Piotroski F-Score with value-based bar colors, Valuation comparison, and Growth CAGR percentages).
   - **Summary (Sheet 2)**: Contains metadata like Company Name, Ticker, Exchange, and the detailed Analyst Brief.
   - **Valuation (Sheet 3)**: Contains multiples like P/E, P/B, EV/EBITDA, and sector comparisons.
   - **Health (Sheet 4)**: Piotroski, Altman, leverage ratios, and liquidity ratings.
   - **Growth (Sheet 5)**: Revenue CAGR, PAT CAGR, margin trends, and FCF yields.
   - **Red Flags (Sheet 6)**: Individual warning details and Beneish M-scores.
2. **`{TICKER}_dashboard.html` (HTML Report, ~12 KB)**:
   - Self-contained dark-theme HTML file utilizing Chart.js.
   - Company profiles, analyst brief, interactive bar charts, and conditional warning flags table.

### When running `telmus compare TICKER_A TICKER_B`:
1. **`{TICKERA}vs{TICKERB}_comparison.xlsx` (Excel Workbook, ~12 KB)**:
   - Side-by-side metric comparison highlighting the winning peer for each parameter (Valuation, Health, Growth).
2. **`{TICKERA}vs{TICKERB}_dashboard.html` (HTML Report, ~15 KB)**:
   - Interactive grouped column charts comparing multiples, health indicators, and growth rates between both tickers side-by-side.

### When running `telmus screen --sector IT`:
1. **`screen_results.xlsx` (Excel Workbook, ~10 KB)**:
   - Summarized table of all companies matching the screen criteria, with averages calculated automatically at the bottom.
2. **`screen_dashboard.html` (HTML Report, ~15 KB)**:
   - Multi-company bar charts comparing quality scores and a sortable data table.

