from __future__ import annotations

import pandas as pd

from valkit.core.result import CompareResult
from valkit.core.scanner import ValkitScanner


def scan(ticker: str):
    return ValkitScanner().scan(ticker)


def compare(ticker_a: str, ticker_b: str) -> CompareResult:
    return ValkitScanner().compare(ticker_a, ticker_b)


def compare_to_dataframe(compare_result: CompareResult) -> pd.DataFrame:
    rows = [
        ("P/E ratio", compare_result.result_a.valuation.pe_ratio, compare_result.result_b.valuation.pe_ratio),
        ("P/B ratio", compare_result.result_a.valuation.pb_ratio, compare_result.result_b.valuation.pb_ratio),
        ("EV/EBITDA", compare_result.result_a.valuation.ev_ebitda, compare_result.result_b.valuation.ev_ebitda),
        ("Piotroski F-score", compare_result.result_a.health.piotroski_f, compare_result.result_b.health.piotroski_f),
        ("Altman Z-score", compare_result.result_a.health.altman_z, compare_result.result_b.health.altman_z),
        ("Revenue CAGR 3y", compare_result.result_a.growth.revenue_cagr_3y, compare_result.result_b.growth.revenue_cagr_3y),
        ("FCF yield", compare_result.result_a.growth.fcf_yield, compare_result.result_b.growth.fcf_yield),
    ]
    return pd.DataFrame(rows, columns=["metric", compare_result.ticker_a, compare_result.ticker_b]).set_index("metric")
