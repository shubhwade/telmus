from __future__ import annotations

import pandas as pd
import pytest

from tellus.core.engines.growth import GrowthEngine, _cagr


def test_cagr_formula_accuracy() -> None:
    assert _cagr(100, 133.1, 3) == pytest.approx(0.10, rel=1e-2)


def test_growth_engine_revenue_cagr_and_margin_trend() -> None:
    income = pd.DataFrame(
        {
            "2024": {"Total Revenue": 133.1, "Net Income": 13.31, "Operating Income": 20},
            "2023": {"Total Revenue": 121.0, "Net Income": 12.1, "Operating Income": 18},
            "2022": {"Total Revenue": 110.0, "Net Income": 11.0, "Operating Income": 16},
            "2021": {"Total Revenue": 100.0, "Net Income": 10.0, "Operating Income": 15},
        }
    ).T
    cashflow = pd.DataFrame({"2024": {"Total Cash From Operating Activities": 40, "Capital Expenditures": 5}}).T
    info = {"marketCap": 100}
    result = GrowthEngine().run({"income_stmt": income, "cashflow": cashflow, "info": info})
    assert isinstance(result.revenue_cagr_3y, float)
    assert result.margin_trend in ("improving", "stable", "declining")


def test_growth_handles_missing_years() -> None:
    income = pd.DataFrame(
        {
            "2024": {"Total Revenue": 150, "Net Income": 15, "Operating Income": 20},
            "2023": {"Total Revenue": 130, "Net Income": 13, "Operating Income": 18},
        }
    ).T
    result = GrowthEngine().run({"income_stmt": income, "cashflow": pd.DataFrame(), "info": {}})
    assert result.revenue_cagr_3y is None
    assert result.pat_cagr_3y is None
