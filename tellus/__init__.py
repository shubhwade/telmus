from __future__ import annotations

from tellus.core.result import ScanResult
from tellus.core.scanner import TellusScanner
from tellus.sdk import compare as compare_scanner, scan as scan_scanner

__all__ = ["TellusScanner", "ScanResult", "scan", "compare"]


def scan(ticker: str) -> ScanResult:
    return scan_scanner(ticker)


def compare(ticker_a: str, ticker_b: str):
    return compare_scanner(ticker_a, ticker_b)
