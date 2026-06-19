# Quickstart

## 1. Install

```bash
pip install valkit
```

## 2. Scan your first ticker

```bash
valkit scan INFY
```

You should see a summary table for valuation, health, and growth metrics, followed by an `analyst_brief` panel.

## 3. Understand the output

- `ticker`: the stock symbol.
- `valuation`: price multiples and sector comparison.
- `health`: Piotroski F-score, Altman Z-score, leverage, and liquidity.
- `growth`: three-year revenue and PAT CAGR, margin trend, and free cash flow yield.
- `red_flags`: any concerning signals.
- `analyst_brief`: deterministic text summarizing strengths and risks.

## 4. Add to Claude Desktop MCP config

```json
{
  "mcpServers": {
    "valkit": {
      "command": "valkit",
      "args": ["serve"],
      "description": "Financial statement analysis — real ratios for any ticker"
    }
  }
}
```

## 5. Ask Claude

Ask: `Analyse INFY financials.`

Claude will call valkit to fetch real financial metrics and provide a grounded answer instead of hallucinating numbers.
