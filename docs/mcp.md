# MCP Server Guide

tellus can run as an MCP server so AI assistants and agents can call financial analytics tools directly. This makes valuation, health, growth, and red-flag metrics available to Claude, Cursor, Windsurf, and other MCP-compatible clients.

## Why use tellus as an MCP server

- Get deterministic financial metrics from real data, not guesses.
- Let AI agents fetch company analysis automatically during conversations.
- Keep your local environment in control while giving assistants structured access to tools.
- Use the same API for both command-line workflows and agent-based integrations.

## Start the server

```bash
tellus serve
```

When the server starts, you should see:

```text
tellus MCP server listening on port 8080
Available tools: scan, scan_ticker, compare, screen, info
```

## Available MCP tools

### `scan(ticker)`

- **Inputs**: `ticker` (string)
- **Purpose**: Run a full financial scan for a single company.
- **Returns**: `valuation`, `health`, `growth`, `flags`, `analyst_brief`

Use this when you want a complete snapshot of one stock.

### `scan_ticker(ticker, exchange)`

- **Inputs**: `ticker` (string), `exchange` (string)
- **Purpose**: Resolve exchange-specific symbols and scan accurately.
- **Returns**: same structured scan result as `scan`

Use this when your assistant needs to distinguish between listings that share a ticker symbol.

### `compare(ticker_a, ticker_b)`

- **Inputs**: `ticker_a` (string), `ticker_b` (string)
- **Purpose**: Compare two companies side by side.
- **Returns**: valuation, health, growth, and analyst summary for both tickers.

Use this for peer analysis or watchlist comparisons.

### `screen(sector, min_piotroski, max_de)`

- **Inputs**:
  - `sector` (string)
  - `min_piotroski` (integer)
  - `max_de` (float)
- **Purpose**: Filter stocks by sector, earnings quality, and leverage.
- **Returns**: a list of matching tickers with their financial metrics.

Use this for building a shortlist of fundamentally stronger companies.

### `info()`

- **Inputs**: none
- **Purpose**: Retrieve server status and metadata.
- **Returns**: version, tool list, data source details, and uptime.

Use this to verify the server is running and to check available tools.

## Client setup examples

### Claude Desktop

```json
{
  "mcpServers": {
    "tellus": {
      "command": "tellus",
      "args": ["serve"],
      "description": "Financial statement analysis - real ratios for any ticker"
    }
  }
}
```

### Cursor

```json
{
  "mcpServers": {
    "tellus": {
      "command": "tellus",
      "args": ["serve"],
      "description": "Financial statement analysis - real ratios for any ticker"
    }
  }
}
```

### Windsurf

```json
{
  "mcpServers": {
    "tellus": {
      "command": "tellus",
      "args": ["serve"],
      "description": "Financial statement analysis - real ratios for any ticker"
    }
  }
}
```

## Using the tools

### Example: scan a company

Ask the assistant to:

- `Analyze INFY financials`
- `Run a scan for AAPL`
- `Get Piotroski and Altman Z for TCS`

### Example: compare two names

Ask the assistant to:

- `Compare INFY and TCS`
- `Show me valuation and health differences between Apple and Microsoft`

### Example: screen for quality companies

Ask the assistant to:

- `Find IT stocks with Piotroski above 6 and debt-to-equity below 1.5`
- `Give me a shortlist of low-leverage, high-quality companies in the technology sector`

## Best practices

- Start with `info()` to confirm the server is running.
- Use `scan()` for detailed company analysis.
- Use `compare()` for direct peer comparisons.
- Use `screen()` to filter a universe before deeper research.
- Use `scan_ticker()` when the assistant needs an exchange-specific symbol.

## Troubleshooting

- If the server does not start, verify that `tellus` is installed and the `serve` command is available.
- If the assistant cannot connect, confirm that the MCP client is configured to launch `tellus serve` and that the local port is open.
- If a ticker cannot be resolved, use `scan_ticker()` with the exchange hint.
