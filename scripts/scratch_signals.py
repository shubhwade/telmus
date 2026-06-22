from telmus.core.loaders import load_financials
from telmus.core.engines.health import HealthEngine
import pandas as pd

ticker = "AAPL"
try:
    financials = load_financials(ticker)
    
    income_stmt = financials.get("income_stmt")
    if income_stmt is None:
        income_stmt = pd.DataFrame()
        
    balance_sheet = financials.get("balance_sheet")
    if balance_sheet is None:
        balance_sheet = pd.DataFrame()
        
    cashflow = financials.get("cashflow")
    if cashflow is None:
        cashflow = pd.DataFrame()

    he = HealthEngine()
    print("ROA Positive:", he._roa_positive(income_stmt, balance_sheet))
    print("CFO Positive:", he._cfo_positive(cashflow))
    print("ROA Improving:", he._roa_increasing(income_stmt, balance_sheet))
    print("Low Accruals:", he._accruals(income_stmt, cashflow))
    print("Leverage Falling:", he._leverage_decreasing(balance_sheet))
    print("Liquidity Rising:", he._liquidity_increasing(balance_sheet))
    print("No Dilution:", he._no_dilution(balance_sheet))
    print("Gross Margin Rising:", he._gross_margin_increasing(income_stmt))
    print("Asset Turnover Rising:", he._asset_turnover_increasing(income_stmt, balance_sheet))
except Exception as e:
    import traceback
    traceback.print_exc()
