from __future__ import annotations

import time

from valkit.core.brief import generate_brief
from valkit.core.engines.flags import FlagsEngine
from valkit.core.engines.growth import GrowthEngine
from valkit.core.engines.health import HealthEngine
from valkit.core.engines.valuation import ValuationEngine
from valkit.core.loaders import load_financials
from valkit.core.result import CompareResult, ScanResult


class ValkitScanner:
    def scan(self, ticker: str) -> ScanResult:
        start = time.time()
        financials = load_financials(ticker)
        valuation = ValuationEngine().run(financials)
        health = HealthEngine().run(financials)
        growth = GrowthEngine().run(financials)
        flags = FlagsEngine().run(financials)
        duration_ms = int((time.time() - start) * 1000)

        company = financials.get("info", {}).get("longName") or financials.get("info", {}).get("shortName") or ticker
        exchange = financials.get("info", {}).get("exchange") or financials.get("info", {}).get("exchangeTimezoneName") or "unknown"
        brief = generate_brief(
            ScanResult(
                ticker=ticker,
                company=company,
                exchange=exchange,
                scan_duration_ms=duration_ms,
                valuation=valuation,
                health=health,
                growth=growth,
                red_flags=flags.red_flags,
                highest_concern=flags.highest_concern,
                analyst_brief="",
            )
        )

        return ScanResult(
            ticker=ticker,
            company=company,
            exchange=exchange,
            scan_duration_ms=duration_ms,
            valuation=valuation,
            health=health,
            growth=growth,
            red_flags=flags.red_flags,
            highest_concern=flags.highest_concern,
            analyst_brief=brief,
        )

    def compare(self, ticker_a: str, ticker_b: str) -> CompareResult:
        result_a = self.scan(ticker_a)
        result_b = self.scan(ticker_b)
        return CompareResult(
            ticker_a=ticker_a,
            ticker_b=ticker_b,
            result_a=result_a,
            result_b=result_b,
        )
