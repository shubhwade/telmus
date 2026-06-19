# tellus

[![PyPI version](https://img.shields.io/pypi/v/tellus)](https://pypi.org/project/tellus/)
[![Downloads](https://img.shields.io/pypi/dm/tellus)](https://pypi.org/project/tellus/)
[![Python](https://img.shields.io/pypi/pyversions/tellus)](https://pypi.org/project/tellus/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

Financial statement analysis for AI IDEs and coding agents.

```bash
pip install tellus
tellus scan INFY
```

## What is tellus?

tellus is a Python package and CLI for parsing financial statements, computing key valuation and health ratios, and exposing them through an MCP server for AI tools. Just as mustel gives AI IDEs ground truth about your code, tellus gives AI IDEs ground truth about financial statements.

## Engines

| Engine | What it measures | Key metric |
|---|---|---|
| Valuation | Price multiples and peer comparison | P/E, P/B, EV/EBITDA |
| Health | Balance sheet strength and bankruptcy risk | Piotroski F-score, Altman Z-score |
| Flags | Earnings quality and cash flow risk | Beneish M-score, free cash flow trend |

## analyst_brief

A deterministic summary field that explains fundamentals, growth, and red flags without using an LLM.

Example output:

```json
{
  "analyst_brief": "Strong fundamentals (Piotroski F-score of 7). Financially safe (Altman Z-score of 4.20). Revenue growth is 11.2% over three years and operating margins are stable. No significant red flags detected. Suitable for DCF or comparable company analysis."
}
```

## Quick start

1. Install:

```bash
pip install tellus
```

2. Scan a ticker:

```bash
tellus scan INFY
```

3. Read the summary and analyst brief, or export JSON for automation.

## MCP server setup

```json
{
  "mcpServers": {
    "tellus": {
      "command": "tellus",
      "args": ["serve"],
      "description": "Financial statement analysis — real ratios for any ticker"
    }
  }
}
```

- Claude Desktop: use the config to register tellus as an MCP tool.
- Cursor: same config loads tellus as a tool for market research.
- Windsurf: connect the MCP server to get real financial metrics.

## Other commands

| Command | Description |
|---|---|
| `tellus scan TICKER` | Run a full financial scan |
| `tellus scan TICKER --json` | Print raw JSON |
| `tellus scan TICKER --export FILE.json` | Save JSON to a file |
| `tellus compare A B` | Compare two tickers |
| `tellus screen` | Run a simple sector screener |
| `tellus serve` | Start the MCP server |
| `tellus info` | Print package info |
| `tellus check TICKER` | Quick health check |

## Benchmark

| Test | Result |
|---|---|
| Piotroski score coverage | 9 signals |
| Altman Z distress detection | safe/grey/distress ranges |
| Flag detection | Beneish M, D/E, FCF trend |

## Architecture

```
yfinance -> loader -> valuation/health/growth/flags -> ScanResult -> CLI / MCP / SDK
```

## Contributing

1. Fork the repository.
2. Create a feature branch.
3. Run `pip install -e ."[dev]"`.
4. Write tests and update docs.
5. Submit a pull request.

## License

MIT License
