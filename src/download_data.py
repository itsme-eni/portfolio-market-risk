from pathlib import Path

import pandas as pd
import yfinance as yf


# These ETFs represent different areas of the financial market.
TICKERS = ["SPY", "QQQ", "AGG", "GLD", "EEM"]

# Fixed dates make the downloaded dataset reproducible.
START_DATE = "2016-01-01"
END_DATE = "2026-10-01"

# Find the project root regardless of where the script is executed from.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = PROJECT_ROOT / "data" / "raw" / "etf_prices.csv"


def download_prices() -> pd.DataFrame:
    """Download daily adjusted closing prices from Yahoo Finance."""

    market_data = yf.download(
        tickers=TICKERS,
        start=START_DATE,
        end=END_DATE,
        interval="1d",
        auto_adjust=True,
        progress=False,
    )

    if market_data.empty:
        raise ValueError("Yahoo Finance returned no market data.")

    # We only need daily closing prices for calculating returns.
    close_prices = market_data["Close"].copy()

    close_prices.index.name = "date"
    close_prices = close_prices.sort_index()

    return close_prices


def save_prices(prices: pd.DataFrame) -> None:
    """Save the downloaded prices as a local CSV file."""

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    prices.to_csv(OUTPUT_PATH)


if __name__ == "__main__":
    prices = download_prices()
    save_prices(prices)

    print("Market data downloaded successfully.")
    print(f"Shape: {prices.shape}")
    print(f"Date range: {prices.index.min()} to {prices.index.max()}")
    print("\nFirst five rows:")
    print(prices.head())