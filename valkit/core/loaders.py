from __future__ import annotations

import functools
import logging

import yfinance as yf

logger = logging.getLogger(__name__)


@functools.lru_cache(maxsize=128)
def load_financials(ticker: str) -> dict[str, object]:
    """Load financial data for a ticker from yfinance.

    Args:
        ticker: Stock ticker symbol.

    Returns:
        A dictionary containing info, income_stmt, balance_sheet, cashflow, fast_info.

    Raises:
        ValueError: If data cannot be loaded for the ticker.
    """
    try:
        ticker_obj = yf.Ticker(ticker)
        info = ticker_obj.info or {}
        income_stmt = ticker_obj.financials if ticker_obj.financials is not None else {}
        balance_sheet = ticker_obj.balance_sheet if ticker_obj.balance_sheet is not None else {}
        cashflow = ticker_obj.cashflow if ticker_obj.cashflow is not None else {}
        fast_info = ticker_obj.fast_info if ticker_obj.fast_info is not None else {}

        if not info and income_stmt == {} and balance_sheet == {} and cashflow == {}:
            raise ValueError(f"No financial data available for ticker '{ticker}'")

        return {
            "info": info,
            "income_stmt": income_stmt,
            "balance_sheet": balance_sheet,
            "cashflow": cashflow,
            "fast_info": fast_info,
        }
    except Exception as exc:
        logger.exception("Failed to load financials for %s", ticker)
        raise ValueError(f"Unable to load financials for ticker '{ticker}': {exc}") from exc
