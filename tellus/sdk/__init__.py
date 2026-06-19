from __future__ import annotations

from tellus.core.scanner import TellusScanner
from tellus.sdk.reconciler import (
    compare_to_dataframe,
    compare as compare_scanner,
    scan as scan_scanner,
)
from tellus.core.result import ScanResult

__all__ = ["TellusScanner", "ScanResult", "scan", "compare", "compare_to_dataframe"]


def scan(ticker: str) -> ScanResult:
    return scan_scanner(ticker)


def compare(ticker_a: str, ticker_b: str) -> object:
    return compare_scanner(ticker_a, ticker_b)
