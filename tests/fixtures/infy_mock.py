from __future__ import annotations

import pandas as pd


def infy_financials() -> dict[str, object]:
    income = pd.DataFrame(
        {
            "2024-03-31": {
                "Total Revenue": 1540000000000,
                "Net Income": 240000000000,
                "Operating Income": 325000000000,
                "Gross Profit": 700000000000,
                "Ebitda": 340000000000,
                "Interest Expense": 5000000000,
                "Selling General Administrative": 120000000000,
                "Depreciation": 45000000000,
            },
            "2023-03-31": {
                "Total Revenue": 1440000000000,
                "Net Income": 220000000000,
                "Operating Income": 305000000000,
                "Gross Profit": 660000000000,
                "Ebitda": 320000000000,
                "Interest Expense": 4800000000,
                "Selling General Administrative": 115000000000,
                "Depreciation": 43000000000,
            },
            "2022-03-31": {
                "Total Revenue": 1320000000000,
                "Net Income": 200000000000,
                "Operating Income": 285000000000,
                "Gross Profit": 620000000000,
                "Ebitda": 300000000000,
                "Interest Expense": 4600000000,
                "Selling General Administrative": 110000000000,
                "Depreciation": 41000000000,
            },
            "2021-03-31": {
                "Total Revenue": 1200000000000,
                "Net Income": 185000000000,
                "Operating Income": 265000000000,
                "Gross Profit": 580000000000,
                "Ebitda": 280000000000,
                "Interest Expense": 4400000000,
                "Selling General Administrative": 105000000000,
                "Depreciation": 39000000000,
            },
        }
    ).T
    balance = pd.DataFrame(
        {
            "2024-03-31": {
                "Total Assets": 1700000000000,
                "Total Current Assets": 550000000000,
                "Total Current Liabilities": 240000000000,
                "Total Liab": 180000000000,
                "Total Stockholder Equity": 1520000000000,
                "Long Term Debt": 10000000000,
                "Cash And Cash Equivalents": 300000000000,
                "Common Stock": 1000000000,
            },
            "2023-03-31": {
                "Total Assets": 1600000000000,
                "Total Current Assets": 530000000000,
                "Total Current Liabilities": 230000000000,
                "Total Liab": 170000000000,
                "Total Stockholder Equity": 1430000000000,
                "Long Term Debt": 11000000000,
                "Cash And Cash Equivalents": 270000000000,
                "Common Stock": 1000000000,
            },
        }
    ).T
    cashflow = pd.DataFrame(
        {
            "2024-03-31": {
                "Total Cash From Operating Activities": 320000000000,
                "Capital Expenditures": 45000000000,
            },
            "2023-03-31": {
                "Total Cash From Operating Activities": 300000000000,
                "Capital Expenditures": 42000000000,
            },
            "2022-03-31": {
                "Total Cash From Operating Activities": 280000000000,
                "Capital Expenditures": 40000000000,
            },
        }
    ).T
    return {
        "info": {
            "symbol": "INFY",
            "longName": "Infosys Limited",
            "exchange": "NSE",
            "marketCap": 2510000000000,
            "sector": "Technology",
        },
        "income_stmt": income,
        "balance_sheet": balance,
        "cashflow": cashflow,
        "fast_info": {"last_price": 153.0},
    }
