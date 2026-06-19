from __future__ import annotations

from valkit.core.result import ScanResult
from valkit.core.scanner import ValkitScanner
from valkit.sdk import compare as compare_scanner, scan as scan_scanner

__all__ = ["ValkitScanner", "ScanResult", "scan", "compare"]


def scan(ticker: str) -> ScanResult:
    return scan_scanner(ticker)


def compare(ticker_a: str, ticker_b: str):
    return compare_scanner(ticker_a, ticker_b)
