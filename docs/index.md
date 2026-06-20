---
template: home.html
---

# telmus

Financial statement analysis for AI IDEs and coding agents.

## Why telmus?

| Engine | What it catches |
|---|---|
| Valuation | Overpriced or undervalued relative to sector peers |
| Health | Balance sheet stress, leverage, and credit risk |
| Flags | Earnings manipulation risk and cash flow trouble |

## Features

- **One Command = Instant Dashboard**: Every scan, compare, or screen command instantly auto-generates styled Excel workbooks and interactive HTML dashboards.
- **50,000+ Tickers Supported Globally**: Seamlessly analyze US, Indian, European, and Asian equities.
- **No API Key Needed**: Pulls data directly from public financial statements automatically.
- **MCP Server Ready**: Built-in Model Context Protocol server for direct integration with AI assistants like Claude Desktop, Cursor, and Windsurf.

## The analyst_brief - The Key Innovation

The `analyst_brief` is a deterministic summary generated from financial metrics and red flags. Designed for AI IDEs to consume without relying on generative models.

```json
{
  "analyst_brief": "Strong fundamentals (Piotroski F-score of 7). Financially safe (Altman Z-score of 4.20). Revenue growth is 11.2% over three years and operating margins are stable. No significant red flags detected. Suitable for DCF or comparable company analysis."
}
```

## Quick start

1. Install: `pip install telmus`
2. Run `telmus scan INFY`
3. Read the summary, ratios, and red flags

## MCP Server

Use telmus as an MCP tool for Claude, Cursor, or any MCP-aware IDE.

```json
{
  "mcpServers": {
    "telmus": {
      "command": "telmus",
      "args": ["serve"],
      "description": "Financial statement analysis - real ratios for any ticker"
    }
  }
}
```