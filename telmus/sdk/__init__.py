from __future__ import annotations

from telmus.core.scanner import TelmusScanner
from telmus.sdk.reconciler import (
    compare_to_dataframe,
    compare as compare_scanner,
    scan as scan_scanner,
)
from telmus.core.result import ScanResult

__all__ = ["TelmusScanner", "ScanResult", "scan", "compare", "compare_to_dataframe"]


def scan(ticker: str) -> ScanResult:
    return scan_scanner(ticker)


def compare(ticker_a: str, ticker_b: str) -> object:
    return compare_scanner(ticker_a, ticker_b)
