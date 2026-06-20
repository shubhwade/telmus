from __future__ import annotations

import csv
import datetime
from telmus.core.scanner import TelmusScanner


class PowerBIExporter:
    def export_portfolio(self, tickers: list[str], path: str) -> None:
        scanner = TelmusScanner()
        today = datetime.date.today().isoformat()

        headers = [
            "Date",
            "Ticker",
            "Company",
            "Exchange",
            "PE_Ratio",
            "PB_Ratio",
            "EV_EBITDA",
            "Sector_Comparison",
            "Piotroski_F",
            "Altman_Z",
            "Debt_Equity",
            "Current_Ratio",
            "Interest_Coverage",
            "Revenue_CAGR_3Y",
            "PAT_CAGR_3Y",
            "Margin_Trend",
            "FCF_Yield",
            "Beneish_M",
            "Red_Flag_Count",
            "Highest_Concern",
            "Analyst_Brief",
        ]

        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(headers)

            for ticker in tickers:
                res = scanner.scan(ticker)
                writer.writerow([
                    today,
                    res.ticker,
                    res.company,
                    res.exchange,
                    self._csv_val(res.valuation.pe_ratio),
                    self._csv_val(res.valuation.pb_ratio),
                    self._csv_val(res.valuation.ev_ebitda),
                    self._csv_val(res.valuation.vs_sector),
                    self._csv_val(res.health.piotroski_f),
                    self._csv_val(res.health.altman_z),
                    self._csv_val(res.health.debt_to_equity),
                    self._csv_val(res.health.current_ratio),
                    self._csv_val(res.health.interest_coverage),
                    self._csv_val(res.growth.revenue_cagr_3y),
                    self._csv_val(res.growth.pat_cagr_3y),
                    self._csv_val(res.growth.margin_trend),
                    self._csv_val(res.growth.fcf_yield),
                    self._csv_val(res.beneish_m),
                    len(res.red_flags),
                    res.highest_concern,
                    res.analyst_brief,
                ])

    def export_flags(self, tickers: list[str], path: str) -> None:
        scanner = TelmusScanner()
        today = datetime.date.today().isoformat()

        headers = ["Date", "Ticker", "Flag_Type", "Flag_Value", "Flag_Severity"]

        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(headers)

            for ticker in tickers:
                res = scanner.scan(ticker)
                if not res.red_flags:
                    writer.writerow([today, res.ticker, "none", "", ""])
                else:
                    for flag in res.red_flags:
                        writer.writerow([
                            today,
                            res.ticker,
                            flag.type,
                            self._csv_val(flag.value),
                            flag.severity,
                        ])

    def _csv_val(self, val: any) -> any:
        if val is None:
            return ""
        return val
