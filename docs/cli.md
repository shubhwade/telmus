# CLI Reference

The `valkit` command-line interface gives you fast access to financial scans, comparisons, screens, health checks, and MCP server mode. Use these commands to analyze companies, compare peers, filter investment candidates, and serve results to AI assistants.

## `valkit scan TICKER [--json] [--export PATH]`

**What it does**
Performs a complete financial scan for a single ticker and returns valuation, health, growth, red-flag metrics, and a deterministic analyst brief.

**When to use it**
- You want a fast company profile for a single stock.
- You need structured JSON output for automation.
- You want an analyst brief that summarizes fundamentals clearly.

**Syntax**
```bash
valkit scan TICKER [--json] [--export PATH]
```

**Examples**
```bash
valkit scan INFY
valkit scan INFY --json
valkit scan INFY --export infy-report.json
```

**Output**
The default output includes sections for `Valuation`, `Health`, `Growth`, and `Analyst brief`. When you use `--json`, the CLI returns a JSON object with nested sections like `valuation`, `health`, `growth`, `flags`, and `analyst_brief`.

**Flags**
- `--json` return the full structured result as JSON.
- `--export PATH` save the scan result to a JSON file at the specified path.

---

## `valkit compare TICKER_A TICKER_B`

**What it does**
Compares two tickers side by side across their financial metrics, making it easy to spot valuation, health, and growth differences.

**When to use it**
- You want a quick peer comparison between two stocks.
- You are choosing between alternatives in the same sector.
- You need a concise view of relative risk and valuation.

**Syntax**
```bash
valkit compare TICKER_A TICKER_B
```

**Example**
```bash
valkit compare INFY TCS
```

**Output**
The comparison table shows metrics such as `P/E`, `P/B`, `EV/EBITDA`, `Piotroski F`, `Altman Z`, `Revenue CAGR 3y`, and `Margin Trend` for both tickers.

---

## `valkit screen [--sector TEXT] [--min-piotroski INT] [--max-de FLOAT]`

**What it does**
Filters the ticker universe by sector, Piotroski score, and leverage, returning only companies that match the selected quality criteria.

**When to use it**
- You want to find fundamentally strong stocks in a specific sector.
- You want to enforce minimum earnings quality and maximum leverage rules.
- You are building a shortlist for deeper analysis.

**Syntax**
```bash
valkit screen [--sector TEXT] [--min-piotroski INT] [--max-de FLOAT]
```

**Example**
```bash
valkit screen --sector IT --min-piotroski 6 --max-de 1.5
```

**Available flags**
- `--sector TEXT` filter by industry sector.
- `--min-piotroski INT` require a minimum Piotroski F-score.
- `--max-de FLOAT` require a maximum debt-to-equity ratio.

---

## `valkit check TICKER`

**What it does**
Runs a compact health check for a ticker and returns the most important balance sheet and earnings quality indicators.

**When to use it**
- You need a quick health snapshot without the full scan.
- You want to confirm whether a company passes basic leverage and liquidity thresholds.
- You are screening for balance-sheet risk.

**Syntax**
```bash
valkit check TICKER
```

**Example**
```bash
valkit check INFY
```

**Output**
The check output focuses on `Piotroski F`, `Altman Z`, `D/E`, `Current Ratio`, and `Interest Coverage`, plus a brief risk summary.

---

## `valkit serve`

**What it does**
Starts valkit in MCP server mode so connected AI tools and assistants can call it as a structured external tool.

**When to use it**
- You want an AI assistant to query real financial metrics automatically.
- You are integrating valkit with an MCP-compatible client such as Claude Desktop, Cursor, or Windsurf.
- You need a live, local tool endpoint for your agent workflows.

**Syntax**
```bash
valkit serve
```

**Example**
```bash
valkit serve
```

**Expected output**
```text
valkit MCP server listening on port 8080
Available tools: scan, scan_ticker, compare, screen, info
```

---

## `valkit info`

**What it does**
Displays server metadata, package version, tool availability, and data source details.

**When to use it**
- You want to verify the running server state.
- You need the current package version or supported tool list.
- You are troubleshooting your MCP service.

**Syntax**
```bash
valkit info
```

**Example**
```bash
valkit info
```

**Sample output**
```text
valkit version: 0.1.0
data source: public financial statements
available tools: scan, scan_ticker, compare, screen, info
```

---

## Common workflows

### Perform a scan and save the result
```bash
valkit scan INFY --export infy.json
```

### Compare two investment candidates
```bash
valkit compare INFY TCS
```

### Start the MCP server for AI integration
```bash
valkit serve
```

### Screen for stronger companies in a sector
```bash
valkit screen --sector IT --min-piotroski 7 --max-de 1.2
```
