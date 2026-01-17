import yfinance as yf
import pandas as pd

# Stock symbol
symbol = "AAPL"

# Download historical data
data = yf.download(
    symbol,
    start="2015-01-01",
    end="2024-12-31",
    interval="1d"   # 1m, 5m, 15m, 1h, 1d, 1wk, 1mo
)

# Save to CSV
data.to_csv(f"{symbol}_historical.csv")

print("CSV downloaded successfully")
