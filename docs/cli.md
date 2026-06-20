# CLI Reference

The `telmus` command-line interface provides instant financial statement analysis. Every main command automatically generates styled Excel workbooks and interactive HTML dashboards.

---

## == SCAN COMMAND ==

```bash
telmus scan TICKER
```

**What it does**
Performs a comprehensive financial scan for a single ticker and generates detailed reports.

**Examples**
- `telmus scan INFY.NS` (Indian NSE stock)
- `telmus scan AAPL` (US stock)
- `telmus scan RELIANCE.NS` (Indian NSE stock)

**Auto-generates instantly after every scan:**
- **`TICKER_analysis.xlsx`**: Excel workbook with 6 sheets, starting with the interactive **Dashboard** tab at index 0 followed by Valuation, Health, Growth, and Red Flags details.
- **`TICKER_dashboard.html`**: A fully self-contained dark-theme HTML report with Chart.js charts that opens automatically in your web browser.

---

## == COMPARE COMMAND ==

```bash
telmus compare TICKER_A TICKER_B
```

**What it does**
Compares two tickers side-by-side across their financial metrics.

**Examples**
- `telmus compare INFY.NS TCS.NS`
- `telmus compare AAPL MSFT`

**Auto-generates:**
- **`TICKERAvsTICKERB_comparison.xlsx`**: Side-by-side comparative Excel workbook.
- **`TICKERAvsTICKERB_dashboard.html`**: Grouped bar charts (Teal for Ticker A, Orange for Ticker B) and a winner-highlighted metrics table. Opens automatically in your browser.

---

## == SCREEN COMMAND ==

```bash
telmus screen [--sector TEXT] [--min-piotroski INT] [--max-de FLOAT]
```

**What it does**
Screens the stock universe using specific filters.

**Examples**
- `telmus screen --sector IT`
- `telmus screen --sector IT --min-piotroski 5`
- `telmus screen --sector IT --max-de 1.5`
- `telmus screen --sector Banking`

**Auto-generates:**
- **`screen_results.xlsx`**: Tabular Excel sheet summarizing all screening results and averages.
- **`screen_dashboard.html`**: Visual comparison dashboard with interactive multi-company bar charts and a sortable results table. Opens automatically in your browser.

---

## == CHECK COMMAND ==

```bash
telmus check TICKER
```

**What it does**
Performs a lightweight, ultra-fast financial safety check on a ticker.

**Examples**
- `telmus check INFY.NS`

**Notes**
- Fast health check only — **no report files are generated**. Prints summary output directly to the terminal.

---

## == POWERBI COMMAND ==

```bash
telmus powerbi --tickers INFY.NS TCS.NS WIPRO.NS --export portfolio.csv
```

**What it does**
Generates custom portfolios formatted for Power BI.

**Auto-generates:**
- **`portfolio.csv`**: A CSV file structured for Power BI data models.
- **`portfolio_report.html`**: A self-contained dark-theme HTML dashboard showcasing the combined portfolio metrics.

---

## == SERVE COMMAND ==

```bash
telmus serve
```

**What it does**
Starts the telmus MCP (Model Context Protocol) server. Useful for connecting telmus as a tool directly to AI assistants like Claude Desktop, Cursor, or Windsurf.

---

## == INFO COMMAND ==

```bash
telmus info
```

**What it does**
Displays system information, including package version, active data sources, and coverage metadata.

---

## Ticker Suffix Conventions

To fetch data correctly from the underlying APIs:
1. **Indian Stocks (NSE)**: Always use the `.NS` suffix (e.g., `INFY.NS`, `TCS.NS`, `RELIANCE.NS`).
2. **Indian Stocks (BSE)**: Use the `.BO` suffix (e.g., `500209.BO`).
3. **US Stocks**: Use no suffix (e.g., `AAPL`, `MSFT`, `GOOGL`).
