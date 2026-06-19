from __future__ import annotations

import pandas as pd

from tellus.core.engines.valuation import ValuationEngine


def test_valuation_with_infy_mock() -> None:
    income = pd.DataFrame({"2024": {"Net Income": 240000000000}}).T
    balance = pd.DataFrame({"2024": {"Total Stockholder Equity": 1200000000000, "Cash And Cash Equivalents": 300000000000, "Long Term Debt": 10000000000}}).T
    financials = {
        "info": {"marketCap": 2500000000000, "sector": "Technology", "symbol": "INFY"},
        "income_stmt": income,
        "balance_sheet": balance,
    }
    result = ValuationEngine().run(financials)
    assert result.pe_ratio is not None and result.pe_ratio > 0
    assert result.pb_ratio is not None and result.pb_ratio > 0
    assert result.ev_ebitda is None or result.ev_ebitda >= 0


def test_vs_sector_returns_expected_category() -> None:
    income = pd.DataFrame({"2024": {"Net Income": 1}}).T
    balance = pd.DataFrame({"2024": {"Total Stockholder Equity": 1, "Cash And Cash Equivalents": 0, "Long Term Debt": 0}}).T
    financials = {
        "info": {"marketCap": 100, "sector": "Technology", "symbol": "INFY"},
        "income_stmt": income,
        "balance_sheet": balance,
    }
    result = ValuationEngine().run(financials)
    assert result.vs_sector in ("cheap", "fair", "expensive", None)


def test_division_by_zero_handled() -> None:
    income = pd.DataFrame({"2024": {"Net Income": 0}}).T
    balance = pd.DataFrame({"2024": {"Total Stockholder Equity": 100}}).T
    financials = {
        "info": {"marketCap": 100, "sector": "Technology", "symbol": "INFY"},
        "income_stmt": income,
        "balance_sheet": balance,
    }
    result = ValuationEngine().run(financials)
    assert result.pe_ratio is None
