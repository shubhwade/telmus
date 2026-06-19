from __future__ import annotations

import logging

import numpy as np
import pandas as pd

from tellus.core.result import FlagsResult, RedFlag

logger = logging.getLogger(__name__)


def _safe_value(value: object) -> float | None:
    if value is None:
        return None
    try:
        value_float = float(value)
    except (TypeError, ValueError):
        return None
    if np.isnan(value_float):
        return None
    return value_float


def _safe_divide(numerator: float | None, denominator: float | None) -> float | None:
    if numerator is None or denominator is None or denominator == 0:
        return None
    return numerator / denominator


def _get_series(df: pd.DataFrame, label: str) -> pd.Series | None:
    if label in df.index:
        return df.loc[label]
    if label in df.columns:
        return df[label]
    return None


class FlagsEngine:
    def run(self, financials: dict[str, object]) -> FlagsResult:
        income_stmt = financials.get("income_stmt")
        if income_stmt is None:
            income_stmt = pd.DataFrame()
        balance_sheet = financials.get("balance_sheet")
        if balance_sheet is None:
            balance_sheet = pd.DataFrame()
        cashflow = financials.get("cashflow")
        if cashflow is None:
            cashflow = pd.DataFrame()

        beneish_m = self._beneish_m_score(income_stmt, balance_sheet, cashflow)
        red_flags: list[RedFlag] = []

        if beneish_m is not None and beneish_m > -2.22:
            red_flags.append(
                RedFlag(type="beneish_m", value=round(beneish_m, 2), severity="high")
            )

        de_ratio = self._de_ratio(balance_sheet)
        if de_ratio is not None and de_ratio > 2.0:
            red_flags.append(
                RedFlag(type="de_ratio", value=round(de_ratio, 2), severity="medium")
            )

        negative_fcf_count = self._negative_fcf_years(cashflow)
        if negative_fcf_count >= 2:
            red_flags.append(
                RedFlag(
                    type="negative_fcf", value=negative_fcf_count, severity="medium"
                )
            )

        highest = "low"
        for flag in red_flags:
            if flag.severity == "high":
                highest = "high"
                break
            if flag.severity == "medium" and highest != "high":
                highest = "medium"

        return FlagsResult(
            red_flags=red_flags, beneish_m=beneish_m, highest_concern=highest
        )

    def _beneish_m_score(
        self,
        income_stmt: pd.DataFrame,
        balance_sheet: pd.DataFrame,
        cashflow: pd.DataFrame,
    ) -> float | None:
        if (
            "Gross Profit" not in income_stmt.index
            or "Total Revenue" not in income_stmt.index
        ):
            logger.warning("Beneish score missing revenue or gross profit")
            return None

        if (
            _get_series(balance_sheet, "Total Assets") is None
            or _get_series(balance_sheet, "Total Current Assets") is None
        ):
            logger.warning("Beneish score missing assets")
            return None

        if _get_series(cashflow, "Total Cash From Operating Activities") is None:
            logger.warning("Beneish score missing cash flow")
            return None

        def val(series: pd.Series, index: int = 0) -> float | None:
            if len(series) <= index:
                return None
            return _safe_value(series.iloc[index])

        try:
            gp_series = _get_series(income_stmt, "Gross Profit")
            rev_series = _get_series(income_stmt, "Total Revenue")
            ta_series = _get_series(balance_sheet, "Total Assets")
            ca_series = _get_series(balance_sheet, "Total Current Assets")
            cfo_series = _get_series(cashflow, "Total Cash From Operating Activities")
            gp0 = val(gp_series, 0) if gp_series is not None else None
            gp1 = val(gp_series, 1) if gp_series is not None else None
            rev0 = val(rev_series, 0) if rev_series is not None else None
            rev1 = val(rev_series, 1) if rev_series is not None else None
            ta0 = val(ta_series, 0) if ta_series is not None else None
            ta1 = val(ta_series, 1) if ta_series is not None else None
            ca0 = val(ca_series, 0) if ca_series is not None else None
            ca1 = val(ca_series, 1) if ca_series is not None else None
            cfo0 = val(cfo_series, 0) if cfo_series is not None else None
            sga_series = _get_series(income_stmt, "Selling General Administrative")
            dep_series = _get_series(income_stmt, "Depreciation")
            xi_series = _get_series(income_stmt, "Interest Expense")
            net_income_series = _get_series(income_stmt, "Net Income")
            sga0 = val(sga_series, 0) if sga_series is not None else None
            sga1 = val(sga_series, 1) if sga_series is not None else None
            dep0 = val(dep_series, 0) if dep_series is not None else None
            dep1 = val(dep_series, 1) if dep_series is not None else None
            xi0 = val(xi_series, 0) if xi_series is not None else None
            xi1 = val(xi_series, 1) if xi_series is not None else None
            net_income0 = (
                val(net_income_series, 0) if net_income_series is not None else None
            )

            dsri = _safe_divide(_safe_divide(gp0, rev0), _safe_divide(gp1, rev1))
            gmi = _safe_divide(
                _safe_divide(rev1 - gp1 if rev1 and gp1 is not None else None, rev1),
                _safe_divide(rev0 - gp0 if rev0 and gp0 is not None else None, rev0),
            )
            aqi = _safe_divide(
                _safe_divide(1 - _safe_divide(ca0, ta0), 1 - _safe_divide(ca1, ta1)),
                1,
            )
            sgi = _safe_divide(rev0, rev1)
            depi = _safe_divide(
                _safe_divide(
                    1 - _safe_divide(dep0, dep0 + gp0),
                    1 - _safe_divide(dep1, dep1 + gp1),
                ),
                1,
            )
            sgai = _safe_divide(_safe_divide(sga0, rev0), _safe_divide(sga1, rev1))
            tata = _safe_divide(
                _safe_value(cfo0 - net_income0)
                if cfo0 is not None and net_income0 is not None
                else None,
                cfo0,
            )
            lvgi = _safe_divide(
                _safe_divide((rev0 - xi0) if rev0 and xi0 is not None else None, rev0),
                _safe_divide((rev1 - xi1) if rev1 and xi1 is not None else None, rev1),
            )

            if None in (dsri, gmi, aqi, sgi, depi, sgai, tata, lvgi):
                logger.warning("Beneish score missing components")
                return None

            return float(
                -4.84
                + 0.92 * dsri
                + 0.528 * gmi
                + 0.404 * aqi
                + 0.892 * sgi
                + 0.115 * depi
                - 0.172 * sgai
                + 4.679 * tata
                - 0.327 * lvgi
            )
        except Exception:
            logger.exception("Failed to compute Beneish M-score")
            return None

    def _de_ratio(self, balance_sheet: pd.DataFrame) -> float | None:
        total_liab_series = _get_series(balance_sheet, "Total Liab")
        total_equity_series = _get_series(balance_sheet, "Total Stockholder Equity")
        if total_liab_series is None or total_equity_series is None:
            logger.warning("D/E ratio missing values")
            return None
        total_liab = _safe_value(total_liab_series.iloc[0])
        total_equity = _safe_value(total_equity_series.iloc[0])
        if total_liab is None or total_equity is None:
            logger.warning("D/E ratio missing values")
            return None
        return _safe_divide(total_liab, total_equity)

    def _negative_fcf_years(self, cashflow: pd.DataFrame) -> int:
        cashflow_series = _get_series(cashflow, "Total Cash From Operating Activities")
        capex_series = _get_series(cashflow, "Capital Expenditures")
        if cashflow_series is None or capex_series is None:
            logger.warning("Negative FCF check missing cash flow or capex")
            return 0
        count = 0
        for i in range(min(3, len(cashflow_series))):
            cfo = _safe_value(cashflow_series.iloc[i])
            capex = _safe_value(capex_series.iloc[i])
            if cfo is None or capex is None:
                continue
            if cfo - capex < 0:
                count += 1
        return count
