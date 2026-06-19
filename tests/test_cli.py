from __future__ import annotations

import json
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from tellus.cli.app import app
from tellus.core.result import ScanResult
from tellus.core.result import ValuationResult, HealthResult, GrowthResult, RedFlag

runner = CliRunner()


def fake_scan_result() -> ScanResult:
    return ScanResult(
        ticker="INFY",
        company="Infosys Limited",
        exchange="NSE",
        scan_duration_ms=100,
        valuation=ValuationResult(pe_ratio=20.0, pb_ratio=5.0, ev_ebitda=15.0, vs_sector="fair", flag=None),
        health=HealthResult(piotroski_f=7, altman_z=4.0, debt_to_equity=0.1, current_ratio=2.0, interest_coverage=40.0, flag=None),
        growth=GrowthResult(revenue_cagr_3y=0.1, pat_cagr_3y=0.09, margin_trend="stable", fcf_yield=0.03, flag=None),
        red_flags=[],
        highest_concern="low",
        analyst_brief="Strong fundamentals.",
    )


def test_info_exits_zero() -> None:
    result = runner.invoke(app, ["info"])
    assert result.exit_code == 0
    assert "Version" in result.output


@patch("tellus.cli.app.TellusScanner.scan")
def test_scan_json_outputs_json(mock_scan) -> None:
    mock_scan.return_value = fake_scan_result()
    result = runner.invoke(app, ["scan", "INFY", "--json"])
    assert result.exit_code == 0
    parsed = json.loads(result.output)
    assert parsed["ticker"] == "INFY"


@patch("tellus.cli.app.TellusScanner.scan")
def test_check_exits_zero(mock_scan) -> None:
    mock_scan.return_value = fake_scan_result()
    result = runner.invoke(app, ["check", "INFY"])
    assert result.exit_code == 0
    assert "Piotroski F-score" in result.output


@patch("tellus.cli.app.TellusScanner.scan")
def test_scan_bad_ticker_handles_error(mock_scan) -> None:
    mock_scan.side_effect = ValueError("Unable to load financials")
    result = runner.invoke(app, ["scan", "BADTICKER"])
    assert result.exit_code == 1
    assert "Error" in result.output
