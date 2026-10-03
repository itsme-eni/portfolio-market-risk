from pathlib import Path

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]

INPUT_PATH = PROJECT_ROOT / "data" / "processed" / "portfolio_history.csv"
OUTPUT_PATH = PROJECT_ROOT / "data" / "processed" / "risk_metrics.csv"

TRADING_DAYS_PER_YEAR = 252
ROLLING_WINDOW = 21


def load_portfolio_history() -> pd.DataFrame:
    """Load the simulated portfolio history."""

    return pd.read_csv(
        INPUT_PATH,
        parse_dates=["date"],
        index_col="date",
    )


def calculate_volatility(
    portfolio_history: pd.DataFrame,
) -> pd.DataFrame:
    """Calculate 21-day rolling annualised volatility."""

    rolling_volatility = (
        portfolio_history["daily_return"]
        .rolling(window=ROLLING_WINDOW)
        .std()
        * np.sqrt(TRADING_DAYS_PER_YEAR)
    )

    portfolio_history["rolling_volatility"] = rolling_volatility

    return portfolio_history


def calculate_drawdown(
    portfolio_history: pd.DataFrame,
) -> pd.DataFrame:
    """Calculate the decline from each previous portfolio peak."""

    portfolio_history["running_peak"] = (
        portfolio_history["portfolio_value"].cummax()
    )

    portfolio_history["drawdown"] = (
        portfolio_history["portfolio_value"]
        / portfolio_history["running_peak"]
        - 1
    )

    return portfolio_history


def save_risk_metrics(portfolio_history: pd.DataFrame) -> None:
    """Save portfolio history with the calculated risk metrics."""

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    portfolio_history.to_csv(OUTPUT_PATH)


if __name__ == "__main__":
    portfolio_history = load_portfolio_history()

    portfolio_history = calculate_volatility(portfolio_history)
    portfolio_history = calculate_drawdown(portfolio_history)

    save_risk_metrics(portfolio_history)

    annualised_volatility = (
        portfolio_history["daily_return"].std()
        * np.sqrt(TRADING_DAYS_PER_YEAR)
    )

    maximum_drawdown = portfolio_history["drawdown"].min()
    maximum_drawdown_date = portfolio_history["drawdown"].idxmin()

    print("Basic risk metrics calculated successfully.")

    print(f"\nAnnualised volatility: {annualised_volatility:.2%}")
    print(f"Maximum drawdown: {maximum_drawdown:.2%}")
    print(f"Maximum drawdown date: {maximum_drawdown_date.date()}")