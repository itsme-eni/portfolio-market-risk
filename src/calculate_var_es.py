from pathlib import Path

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]

INPUT_PATH = PROJECT_ROOT / "data" / "processed" / "risk_metrics.csv"
OUTPUT_PATH = PROJECT_ROOT / "data" / "processed" / "var_es_metrics.csv"

CONFIDENCE_LEVEL = 0.95
LOOKBACK_WINDOW = 252


def load_portfolio_history() -> pd.DataFrame:
    """Load the portfolio history and existing risk metrics."""

    return pd.read_csv(
        INPUT_PATH,
        parse_dates=["date"],
        index_col="date",
    )


def calculate_expected_shortfall(
    losses: np.ndarray,
) -> float:
    """Calculate the average loss beyond the VaR threshold."""

    var_threshold = np.quantile(losses, CONFIDENCE_LEVEL)

    extreme_losses = losses[losses >= var_threshold]

    return extreme_losses.mean()


def calculate_var_and_es(
    portfolio_history: pd.DataFrame,
) -> pd.DataFrame:
    """Calculate rolling historical VaR and Expected Shortfall."""

    # A negative return becomes a positive loss.
    historical_losses = -portfolio_history["daily_return"].shift(1)

    rolling_losses = historical_losses.rolling(
        window=LOOKBACK_WINDOW,
        min_periods=LOOKBACK_WINDOW,
    )

    portfolio_history["var_95_return"] = rolling_losses.quantile(
        CONFIDENCE_LEVEL
    )

    portfolio_history["expected_shortfall_95_return"] = (
        rolling_losses.apply(
            calculate_expected_shortfall,
            raw=True,
        )
    )

    portfolio_history["var_95_amount"] = (
        portfolio_history["var_95_return"]
        * portfolio_history["portfolio_value"]
    )

    portfolio_history["expected_shortfall_95_amount"] = (
        portfolio_history["expected_shortfall_95_return"]
        * portfolio_history["portfolio_value"]
    )

    return portfolio_history


def save_var_es_metrics(portfolio_history: pd.DataFrame) -> None:
    """Save the portfolio history with VaR and Expected Shortfall."""

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    portfolio_history.to_csv(OUTPUT_PATH)


if __name__ == "__main__":
    portfolio_history = load_portfolio_history()

    portfolio_history = calculate_var_and_es(portfolio_history)

    save_var_es_metrics(portfolio_history)

    available_estimates = portfolio_history.dropna(
        subset=["var_95_return"]
    )

    latest = available_estimates.iloc[-1]

    print("VaR and Expected Shortfall calculated successfully.")

    print(f"\n95% one-day VaR: {latest['var_95_return']:.2%}")
    print(f"95% one-day VaR amount: ${latest['var_95_amount']:,.2f}")

    print(
        "95% Expected Shortfall: "
        f"{latest['expected_shortfall_95_return']:.2%}"
    )
    print(
        "95% Expected Shortfall amount: "
        f"${latest['expected_shortfall_95_amount']:,.2f}"
    )