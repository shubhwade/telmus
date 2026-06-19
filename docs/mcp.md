# MCP Server

## What is MCP?

MCP is a protocol for AI tools to call external tools over a structured interface. valkit exposes financial analysis through MCP so that AI IDEs can use real company ratios instead of guessing.

## Tools

| Tool | Input | Output |
|---|---|---|
| `scan` | `ticker` | Full `ScanResult` JSON |
| `scan_ticker` | `ticker`, `exchange` | Full `ScanResult` JSON |
| `compare` | `ticker_a`, `ticker_b` | Comparison JSON |
| `screen` | `sector`, `min_piotroski`, `max_de` | List of matching scan results |
| `info` | none | Version and data source metadata |

## Claude Desktop config

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

## Cursor config

```json
{
  "mcpServers": {
    "valkit": {
      "command": "valkit",
      "args": ["serve"],
      "description": "Financial statement analysis for Cursor"
    }
  }
}
```

## Windsurf config

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

## Example

Ask the assistant: `What is INFY's financial health?`

The assistant calls the `scan` tool and returns a response grounded in real financial metrics.
