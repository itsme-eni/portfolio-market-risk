from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
INPUT_PATH = PROJECT_ROOT / "data" / "raw" / "etf_prices.csv"

EXPECTED_TICKERS = {"SPY", "QQQ", "AGG", "GLD", "EEM"}


def load_prices() -> pd.DataFrame:
    """Load the raw ETF prices downloaded from Yahoo Finance."""

    if not INPUT_PATH.exists():
        raise FileNotFoundError(
            "Price file not found. Run src/download_data.py first."
        )

    prices = pd.read_csv(
        INPUT_PATH,
        parse_dates=["date"],
        index_col="date",
    )

    return prices


def validate_prices(prices: pd.DataFrame) -> None:
    """Perform basic data-quality checks on the ETF price dataset."""

    print("DATASET SUMMARY")
    print(f"Rows: {len(prices)}")
    print(f"Columns: {len(prices.columns)}")
    print(f"Date range: {prices.index.min()} to {prices.index.max()}")
    print(f"Tickers: {list(prices.columns)}")

    print("\nDATA-QUALITY CHECKS")

    # Check whether all expected ETFs are present.
    missing_tickers = EXPECTED_TICKERS - set(prices.columns)
    print(f"Missing tickers: {missing_tickers}")

    # Check whether any date appears more than once.
    duplicate_dates = prices.index.duplicated().sum()
    print(f"Duplicate dates: {duplicate_dates}")

    # Check whether the observations are chronologically ordered.
    print(f"Dates correctly ordered: {prices.index.is_monotonic_increasing}")

    # Count missing prices separately for every ETF.
    print("\nMissing values per ticker:")
    print(prices.isna().sum())

    # Prices cannot realistically be zero or negative.
    non_positive_prices = (prices <= 0).sum()
    print("\nZero or negative prices per ticker:")
    print(non_positive_prices)

    # Look for extremely large one-day movements that may indicate data problems.
    daily_returns = prices.pct_change(fill_method=None)
    extreme_movements = (daily_returns.abs() > 0.30).sum()

    print("\nDaily movements larger than 30%:")
    print(extreme_movements)


if __name__ == "__main__":
    prices = load_prices()
    validate_prices(prices)