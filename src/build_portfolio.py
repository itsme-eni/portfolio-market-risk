from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]

INPUT_PATH = PROJECT_ROOT / "data" / "raw" / "etf_prices.csv"
OUTPUT_PATH = PROJECT_ROOT / "data" / "processed" / "portfolio_history.csv"

INITIAL_PORTFOLIO_VALUE = 100_000

WEIGHTS = {
    "SPY": 0.35,
    "QQQ": 0.20,
    "AGG": 0.20,
    "GLD": 0.15,
    "EEM": 0.10,
}


def load_prices() -> pd.DataFrame:
    """Load the adjusted ETF prices."""

    return pd.read_csv(
        INPUT_PATH,
        parse_dates=["date"],
        index_col="date",
    )


def calculate_holdings(prices: pd.DataFrame) -> pd.Series:
    """Calculate how many shares are purchased on the first day."""

    weights = pd.Series(WEIGHTS)

    if not weights.sum() == 1:
        raise ValueError("Portfolio weights must add up to 1.")

    initial_allocations = weights * INITIAL_PORTFOLIO_VALUE
    initial_prices = prices.iloc[0]

    shares = initial_allocations / initial_prices

    return shares


def build_portfolio_history(
    prices: pd.DataFrame,
    shares: pd.Series,
) -> pd.DataFrame:
    """Calculate the portfolio value, daily return and daily P&L."""

    asset_values = prices.multiply(shares, axis="columns")
    portfolio_value = asset_values.sum(axis="columns")

    portfolio_history = pd.DataFrame(index=prices.index)
    portfolio_history["portfolio_value"] = portfolio_value
    portfolio_history["daily_return"] = portfolio_value.pct_change()
    portfolio_history["daily_pnl"] = portfolio_value.diff()

    return portfolio_history


def save_portfolio_history(portfolio_history: pd.DataFrame) -> None:
    """Save the portfolio history as a CSV file."""

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    portfolio_history.to_csv(OUTPUT_PATH)


if __name__ == "__main__":
    prices = load_prices()
    shares = calculate_holdings(prices)
    portfolio_history = build_portfolio_history(prices, shares)
    save_portfolio_history(portfolio_history)

    print("Portfolio created successfully.")

    print("\nInitial ETF holdings:")
    print(shares)

    print("\nFirst five portfolio observations:")
    print(portfolio_history.head())

    print("\nFinal portfolio value:")
    print(f"${portfolio_history['portfolio_value'].iloc[-1]:,.2f}")