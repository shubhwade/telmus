from __future__ import annotations

import asyncio
import json
from typing import Any

import mcp.types as types
from mcp.server import NotificationOptions, Server
from mcp.server.stdio import stdio_server

from tellus.core.scanner import TellusScanner

server = Server(
    "tellus",
    version="0.1.0",
    instructions="Financial statement analysis MCP server for AI IDEs.",
)

TOOL_DEFINITIONS: list[types.Tool] = [
    types.Tool(
        name="scan",
        title="Scan ticker",
        description="Run a financial scan for a single ticker symbol.",
        inputSchema={
            "type": "object",
            "properties": {"ticker": {"type": "string"}},
            "required": ["ticker"],
            "additionalProperties": False,
        },
        outputSchema={"type": "object"},
    ),
    types.Tool(
        name="scan_ticker",
        title="Scan ticker with exchange",
        description="Run a financial scan for a ticker symbol and optional exchange.",
        inputSchema={
            "type": "object",
            "properties": {
                "ticker": {"type": "string"},
                "exchange": {"type": "string"},
            },
            "required": ["ticker"],
            "additionalProperties": False,
        },
        outputSchema={"type": "object"},
    ),
    types.Tool(
        name="compare",
        title="Compare two tickers",
        description="Compare financial metrics for two ticker symbols.",
        inputSchema={
            "type": "object",
            "properties": {
                "ticker_a": {"type": "string"},
                "ticker_b": {"type": "string"},
            },
            "required": ["ticker_a", "ticker_b"],
            "additionalProperties": False,
        },
        outputSchema={"type": "object"},
    ),
    types.Tool(
        name="screen",
        title="Screen sector tickers",
        description="Run a simple sector screener and return matching tickers.",
        inputSchema={
            "type": "object",
            "properties": {
                "sector": {"type": "string"},
                "min_piotroski": {"type": "number"},
                "max_de": {"type": "number"},
            },
            "required": [],
            "additionalProperties": False,
        },
        outputSchema={"type": "object"},
    ),
    types.Tool(
        name="info",
        title="Server info",
        description="Return basic server metadata and coverage information.",
        inputSchema={
            "type": "object",
            "properties": {},
            "additionalProperties": False,
        },
        outputSchema={"type": "object"},
    ),
]


def _scan_and_serialize(scanner: TellusScanner, ticker: str) -> str:
    result = scanner.scan(ticker)
    return result.to_json()


async def _serialized_tool_result(payload: dict[str, Any]) -> types.CallToolResult:
    return types.CallToolResult(
        content=[types.TextContent(type="text", text=json.dumps(payload, indent=2))],
        structuredContent=payload,
        isError=False,
    )


@server.list_tools()
async def list_tools(_: types.ListToolsRequest | None = None) -> types.ListToolsResult:
    return types.ListToolsResult(tools=TOOL_DEFINITIONS)


@server.call_tool(validate_input=False)
async def handle_tool_call(
    name: str, arguments: dict[str, Any] | None
) -> types.CallToolResult:
    arguments = arguments or {}
    if name == "scan":
        ticker = arguments.get("ticker")
        if not ticker:
            raise ValueError("Missing ticker")
        payload = {"result": json.loads(_scan_and_serialize(TellusScanner(), ticker))}
    elif name == "scan_ticker":
        ticker = arguments.get("ticker")
        if not ticker:
            raise ValueError("Missing ticker")
        payload = {"result": json.loads(_scan_and_serialize(TellusScanner(), ticker))}
    elif name == "compare":
        ticker_a = arguments.get("ticker_a")
        ticker_b = arguments.get("ticker_b")
        if not ticker_a or not ticker_b:
            raise ValueError("Missing ticker_a or ticker_b")
        comparison = TellusScanner().compare(ticker_a, ticker_b)
        payload = {"result": json.loads(comparison.to_json())}
    elif name == "screen":
        sector = arguments.get("sector", "IT")
        min_piotroski = int(arguments.get("min_piotroski", 0))
        max_de = float(arguments.get("max_de", 10.0))
        universe = {
            "IT": ["INFY", "TCS", "WIPRO", "HCLTECH", "TECHM"],
            "Banking": ["HDFCBANK", "ICICIBANK", "KOTAKBANK", "SBIN", "AXISBANK"],
        }
        tickers = universe.get(sector, universe["IT"])
        scanner = TellusScanner()
        matches: list[dict[str, Any]] = []
        for ticker in tickers:
            result = scanner.scan(ticker)
            if (
                result.health.piotroski_f is None
                or result.health.debt_to_equity is None
            ):
                continue
            if (
                result.health.piotroski_f >= min_piotroski
                and result.health.debt_to_equity <= max_de
            ):
                matches.append(result.to_dict())
        payload = {"matches": matches}
    elif name == "info":
        payload = {
            "version": "0.1.0",
            "data_source": "yfinance",
            "coverage": ["valuation", "health", "growth", "flags"],
            "description": "Financial statement analysis MCP server for AI IDEs.",
        }
    else:
        raise ValueError(f"Unknown tool: {name}")

    return await _serialized_tool_result(payload)


def run_mcp_server() -> None:
    async def run_server() -> None:
        async with stdio_server() as (read_stream, write_stream):
            init_options = server.create_initialization_options(NotificationOptions())
            await server.run(read_stream, write_stream, init_options)

    asyncio.run(run_server())
