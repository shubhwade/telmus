#!/usr/bin/env python
"""
RAW MCP TOOL RESPONSE: scan("INFY")
Detailed output from direct Python execution
"""

import json
import asyncio
from valkit.mcp.server import handle_tool_call

async def show_raw_scan_response():
    """Display the raw JSON response from scan("INFY")."""
    print("=" * 80)
    print("RAW MCP TOOL CALL: scan('INFY')")
    print("=" * 80)
    print("\nInput Parameters:")
    print(json.dumps({"ticker": "INFY"}, indent=2))
    
    print("\n" + "-" * 80)
    print("Processing...")
    print("-" * 80 + "\n")
    
    # Call the tool
    result = await handle_tool_call("scan", {"ticker": "INFY"})
    
    # Get the raw response
    raw_response = result.content[0].text if result.content else "{}"
    response_json = json.loads(raw_response)
    
    print("Raw Response JSON:")
    print(json.dumps(response_json, indent=2))
    
    print("\n" + "=" * 80)
    print("STRUCTURED ANALYSIS")
    print("=" * 80)
    
    result_obj = response_json.get("result", {})
    
    print(f"\nCompany Information:")
    print(f"  - Ticker: {result_obj.get('ticker')}")
    print(f"  - Company: {result_obj.get('company')}")
    print(f"  - Exchange: {result_obj.get('exchange')}")
    print(f"  - Sector: {result_obj.get('sector')}")
    print(f"  - Industry: {result_obj.get('industry')}")
    print(f"  - Market Cap: ${result_obj.get('market_cap', 'N/A'):,}")
    print(f"  - Latest Price: ${result_obj.get('latest_price', 'N/A')}")
    
    print(f"\nValuation Metrics:")
    valuation = result_obj.get('valuation', {})
    for key, value in valuation.items():
        print(f"  - {key}: {value}")
    
    print(f"\nHealth Metrics:")
    health = result_obj.get('health', {})
    for key, value in health.items():
        print(f"  - {key}: {value}")
    
    print(f"\nGrowth Metrics:")
    growth = result_obj.get('growth', {})
    for key, value in growth.items():
        print(f"  - {key}: {value}")
    
    print(f"\nRed Flags:")
    red_flags = result_obj.get('red_flags', [])
    if red_flags:
        for flag in red_flags:
            print(f"  - {flag}")
    else:
        print("  - None detected")
    
    print(f"\nAnalyst Brief:")
    brief = result_obj.get('analyst_brief', '')
    print(f"  {brief}")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    asyncio.run(show_raw_scan_response())
