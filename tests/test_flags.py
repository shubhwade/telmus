from __future__ import annotations

import pandas as pd

from telmus.core.engines.flags import FlagsEngine


def test_beneish_m_returns_float() -> None:
    income = pd.DataFrame(
        {
            "2024": {"Total Revenue": 133.1, "Gross Profit": 50, "Net Income": 10, "Selling General Administrative": 5, "Depreciation": 2, "Interest Expense": 1},
            "2023": {"Total Revenue": 120.0, "Gross Profit": 45, "Net Income": 9, "Selling General Administrative": 4.5, "Depreciation": 1.8, "Interest Expense": 0.9},
        }
    ).T
    balance = pd.DataFrame(
        {
            "2024": {"Total Assets": 100, "Total Current Assets": 40, "Total Liab": 50, "Total Stockholder Equity": 50},
            "2023": {"Total Assets": 90, "Total Current Assets": 35, "Total Liab": 45, "Total Stockholder Equity": 45},
        }
    ).T
    cashflow = pd.DataFrame(
        {
            "2024": {"Total Cash From Operating Activities": 20, "Capital Expenditures": 3},
            "2023": {"Total Cash From Operating Activities": 18, "Capital Expenditures": 2.5},
        }
    ).T
    result = FlagsEngine().run({"income_stmt": income, "balance_sheet": balance, "cashflow": cashflow})
    assert result.beneish_m is None or isinstance(result.beneish_m, float)


def test_high_de_flag_triggered() -> None:
    balance = pd.DataFrame({"2024": {"Total Liab": 250, "Total Stockholder Equity": 100}}).T
    result = FlagsEngine().run({"balance_sheet": balance, "income_stmt": pd.DataFrame(), "cashflow": pd.DataFrame()})
    assert any(flag.type == "de_ratio" for flag in result.red_flags)
    assert result.highest_concern in ("medium", "high", "low")


def test_no_flags_for_clean_mock() -> None:
    income = pd.DataFrame(
        {
            "2024": {"Total Revenue": 100, "Gross Profit": 50, "Net Income": 10, "Selling General Administrative": 5, "Depreciation": 2, "Interest Expense": 1},
            "2023": {"Total Revenue": 95, "Gross Profit": 48, "Net Income": 9.5, "Selling General Administrative": 4.8, "Depreciation": 1.9, "Interest Expense": 1},
        }
    ).T
    balance = pd.DataFrame(
        {
            "2024": {"Total Assets": 100, "Total Current Assets": 40, "Total Liab": 20, "Total Stockholder Equity": 80},
            "2023": {"Total Assets": 95, "Total Current Assets": 38, "Total Liab": 18, "Total Stockholder Equity": 77},
        }
    ).T
    cashflow = pd.DataFrame(
        {
            "2024": {"Total Cash From Operating Activities": 25, "Capital Expenditures": 5},
            "2023": {"Total Cash From Operating Activities": 24, "Capital Expenditures": 4.5},
        }
    ).T
    result = FlagsEngine().run({"income_stmt": income, "balance_sheet": balance, "cashflow": cashflow})
    assert result.red_flags == []
    assert result.highest_concern == "low"
