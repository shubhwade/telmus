import yfinance as yf
import pandas as pd
ticker = yf.Ticker("AAPL")
try:
    print(ticker.income_stmt.head())
    hist = ticker.history(period="5y")
    print(hist.head())
except Exception as e:
    print(e)
