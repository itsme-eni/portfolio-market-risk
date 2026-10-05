from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]

INPUT_PATH = PROJECT_ROOT / "data" / "raw" / "etf_prices.csv"
OUTPUT_PATH = PROJECT_ROOT / "data" / "processed" / "portfolio_exposure.csv"

INITIAL_PORTFOLIO_VALUE = 100_000

PORTFOLIO_WEIGHTS = {
    "SPY": 0.35,
    "QQQ": 0.20,
    "AGG": 0.20,
    "GLD": 0.15,
    "EEM": 0.10,
}


def load_prices() -> pd.DataFrame:
    """Load the historical ETF prices."""

    return pd.read_csv(
        INPUT_PATH,
        parse_dates=["date"],
        index_col="date",
    )


def calculate_units(prices: pd.DataFrame) -> pd.Series:
    """Calculate how many units of each ETF were purchased initially."""

    initial_prices = prices.iloc[0]
    weights = pd.Series(PORTFOLIO_WEIGHTS)

    initial_investment_per_etf = INITIAL_PORTFOLIO_VALUE * weights
    units = initial_investment_per_etf / initial_prices

    return units


def calculate_exposure(
    prices: pd.DataFrame,
    units: pd.Series,
) -> pd.DataFrame:
    """Calculate the value and percentage exposure of every ETF over time."""

    asset_values = prices.mul(units, axis="columns")
    portfolio_value = asset_values.sum(axis=1)

    percentage_exposure = asset_values.div(
        portfolio_value,
        axis="index",
    )

    value_columns = asset_values.add_suffix("_value")
    exposure_columns = percentage_exposure.add_suffix("_exposure")

    exposure_history = pd.concat(
        [
            portfolio_value.rename("portfolio_value"),
            value_columns,
            exposure_columns,
        ],
        axis=1,
    )

    return exposure_history


def save_exposure(exposure_history: pd.DataFrame) -> None:
    """Save the portfolio exposure history."""

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    exposure_history.to_csv(OUTPUT_PATH)


if __name__ == "__main__":
    prices = load_prices()
    units = calculate_units(prices)
    exposure_history = calculate_exposure(prices, units)
    save_exposure(exposure_history)

    print("Portfolio exposure calculated successfully.")

    print("\nInitial ETF units:")
    print(units)

    print("\nLatest percentage exposure:")
    latest_exposure = exposure_history.filter(
        like="_exposure"
    ).iloc[-1]
    print(latest_exposure.map(lambda value: f"{value:.2%}"))