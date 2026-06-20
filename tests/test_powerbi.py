from __future__ import annotations

import csv
import os
import tempfile
from unittest.mock import patch, MagicMock

from telmus.core.result import ScanResult, ValuationResult, HealthResult, GrowthResult, RedFlag
from telmus.exporters.powerbi import PowerBIExporter


def mock_scan_result(ticker: str) -> ScanResult:
    if ticker == "AAPL":
        return ScanResult(
            ticker="AAPL",
            company="Apple Inc.",
            exchange="NASDAQ",
            scan_duration_ms=100,
            valuation=ValuationResult(
                pe_ratio=28.5,
                pb_ratio=10.2,
                ev_ebitda=20.0,
                vs_sector="expensive",
                flag=None
            ),
            health=HealthResult(
            piotroski_f=7, piotroski_signals={'ROA Positive': True, 'CFO Positive': True, 'ROA Improving': True, 'Low Accruals': True, 'Leverage Falling': True, 'Liquidity Rising': True, 'No Dilution': True, 'Gross Margin Rising': False, 'Asset Turnover Rising': False},
                altman_z=4.2,
                debt_to_equity=0.5,
                current_ratio=1.5,
                interest_coverage=8.0,
                flag=None
            ),
            growth=GrowthResult(
                revenue_cagr_3y=0.10,
                pat_cagr_3y=0.12,
                margin_trend="stable",
                fcf_yield=0.06,
                flag=None
            ),
            red_flags=[
                RedFlag(type="expensive_pe", value=28.5, severity="medium")
            ],
            highest_concern="medium",
            analyst_brief="Good health.",
            beneish_m=-2.8
        )
    else:  # Empty ticker mock
        return ScanResult(
            ticker="XYZ",
            company="XYZ Corp",
            exchange="NYSE",
            scan_duration_ms=0,
            valuation=ValuationResult(None, None, None, None, None),
            health=HealthResult(None, {}, None, None, None, None, None),
            growth=GrowthResult(None, None, None, None, None),
            red_flags=[],
            highest_concern="low",
            analyst_brief="No summary.",
            beneish_m=None
        )


@patch("telmus.exporters.powerbi.TelmusScanner")
def test_powerbi_export_portfolio(mock_scanner_class: MagicMock) -> None:
    mock_scanner = mock_scanner_class.return_value
    mock_scanner.scan.side_effect = mock_scan_result

    exporter = PowerBIExporter()
    with tempfile.TemporaryDirectory() as tmpdir:
        csv_path = os.path.join(tmpdir, "portfolio.csv")
        exporter.export_portfolio(["AAPL", "XYZ"], csv_path)

        assert os.path.exists(csv_path)

        with open(csv_path, "r", newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            rows = list(reader)

        # Header check
        assert len(rows) == 3
        headers = rows[0]
        assert headers[1] == "Ticker"
        assert headers[4] == "PE_Ratio"
        assert headers[17] == "Beneish_M"
        assert headers[18] == "Red_Flag_Count"

        # Ticker 1 data check (AAPL)
        row_aapl = rows[1]
        assert row_aapl[1] == "AAPL"
        assert row_aapl[2] == "Apple Inc."
        assert row_aapl[4] == "28.5"
        assert row_aapl[17] == "-2.8"
        assert row_aapl[18] == "1"

        # Ticker 2 data check (XYZ - Nulls)
        row_xyz = rows[2]
        assert row_xyz[1] == "XYZ"
        assert row_xyz[4] == ""  # Null represented as empty string
        assert row_xyz[17] == ""
        assert row_xyz[18] == "0"


@patch("telmus.exporters.powerbi.TelmusScanner")
def test_powerbi_export_flags(mock_scanner_class: MagicMock) -> None:
    mock_scanner = mock_scanner_class.return_value
    mock_scanner.scan.side_effect = mock_scan_result

    exporter = PowerBIExporter()
    with tempfile.TemporaryDirectory() as tmpdir:
        csv_path = os.path.join(tmpdir, "flags.csv")
        exporter.export_flags(["AAPL", "XYZ"], csv_path)

        assert os.path.exists(csv_path)

        with open(csv_path, "r", newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            rows = list(reader)

        # We expect: header + 1 flag for AAPL + 1 "none" flag for XYZ = 3 rows
        assert len(rows) == 3
        headers = rows[0]
        assert headers == ["Date", "Ticker", "Flag_Type", "Flag_Value", "Flag_Severity"]

        # Row 1: AAPL
        assert rows[1][1] == "AAPL"
        assert rows[1][2] == "expensive_pe"
        assert rows[1][3] == "28.5"
        assert rows[1][4] == "medium"

        # Row 2: XYZ (no flags -> "none")
        assert rows[2][1] == "XYZ"
        assert rows[2][2] == "none"
        assert rows[2][3] == ""
        assert rows[2][4] == ""
