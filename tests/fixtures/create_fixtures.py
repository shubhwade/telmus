"""Run once: python tests/fixtures/create_fixtures.py"""

import json

import yfinance as yf


def _dump_ticker(ticker: str, path: str) -> None:
    ticker_obj = yf.Ticker(ticker)
    data = {
        "info": ticker_obj.info,
        "financials": ticker_obj.financials.to_dict() if ticker_obj.financials is not None else {},
        "balance_sheet": ticker_obj.balance_sheet.to_dict() if ticker_obj.balance_sheet is not None else {},
        "cashflow": ticker_obj.cashflow.to_dict() if ticker_obj.cashflow is not None else {},
        "fast_info": ticker_obj.fast_info if ticker_obj.fast_info is not None else {},
    }
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2)


def main() -> None:
    _dump_ticker("INFY", "tests/fixtures/infy_financials.json")
    _dump_ticker("TCS", "tests/fixtures/tcs_financials.json")


if __name__ == "__main__":
    main()
