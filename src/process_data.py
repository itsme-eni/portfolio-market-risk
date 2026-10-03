from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]

INPUT_PATH = PROJECT_ROOT / "data" / "raw" / "etf_prices.csv"
OUTPUT_PATH = PROJECT_ROOT / "data" / "processed" / "daily_returns.csv"


def load_prices() -> pd.DataFrame:
    """Load validated ETF closing prices."""

    prices = pd.read_csv(
        INPUT_PATH,
        parse_dates=["date"],
        index_col="date",
    )

    return prices


def calculate_daily_returns(prices: pd.DataFrame) -> pd.DataFrame:
    """Calculate the percentage change in price between consecutive days."""

    daily_returns = prices.pct_change(fill_method=None)

    # The first day has no previous day for comparison, so its return is missing.
    daily_returns = daily_returns.dropna()

    return daily_returns


def save_returns(daily_returns: pd.DataFrame) -> None:
    """Save the processed daily returns."""

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    daily_returns.to_csv(OUTPUT_PATH)


if __name__ == "__main__":
    prices = load_prices()
    daily_returns = calculate_daily_returns(prices)
    save_returns(daily_returns)

    print("Daily returns calculated successfully.")
    print(f"Shape: {daily_returns.shape}")
    print(f"Date range: {daily_returns.index.min()} to {daily_returns.index.max()}")

    print("\nFirst five rows:")
    print(daily_returns.head())

    print("\nMinimum daily return per ticker:")
    print(daily_returns.min())

    print("\nMaximum daily return per ticker:")
    print(daily_returns.max())