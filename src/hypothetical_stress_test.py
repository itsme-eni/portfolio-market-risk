from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]

INPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "portfolio_exposure.csv"
)

OUTPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "hypothetical_stress_tests.csv"
)

TICKERS = ["SPY", "QQQ", "AGG", "GLD", "EEM"]

STRESS_SCENARIOS = {
    "Equity market crash": {
        "SPY": -0.20,
        "QQQ": -0.25,
        "AGG": 0.03,
        "GLD": 0.08,
        "EEM": -0.25,
    },
    "Interest-rate shock": {
        "SPY": -0.08,
        "QQQ": -0.12,
        "AGG": -0.10,
        "GLD": -0.05,
        "EEM": -0.10,
    },
    "Global risk-off event": {
        "SPY": -0.15,
        "QQQ": -0.20,
        "AGG": 0.05,
        "GLD": 0.10,
        "EEM": -0.25,
    },
    "Severe liquidity crisis": {
        "SPY": -0.25,
        "QQQ": -0.30,
        "AGG": -0.08,
        "GLD": -0.05,
        "EEM": -0.30,
    },
}


def load_portfolio_exposure() -> pd.DataFrame:
    """Load the portfolio's value and exposure history."""

    return pd.read_csv(
        INPUT_PATH,
        parse_dates=["date"],
        index_col="date",
    )


def calculate_stress_scenario(
    current_values: pd.Series,
    scenario_name: str,
    shocks: dict,
) -> dict:
    """Apply hypothetical ETF price shocks to the current portfolio."""

    shock_series = pd.Series(shocks)

    asset_pnl = current_values * shock_series
    stressed_values = current_values + asset_pnl

    current_portfolio_value = current_values.sum()
    stressed_portfolio_value = stressed_values.sum()

    portfolio_pnl = (
        stressed_portfolio_value - current_portfolio_value
    )

    portfolio_return = (
        portfolio_pnl / current_portfolio_value
    )

    result = {
        "scenario": scenario_name,
        "current_portfolio_value": current_portfolio_value,
        "stressed_portfolio_value": stressed_portfolio_value,
        "portfolio_pnl": portfolio_pnl,
        "portfolio_return": portfolio_return,
    }

    for ticker in TICKERS:
        result[f"{ticker}_shock"] = shock_series[ticker]
        result[f"{ticker}_pnl"] = asset_pnl[ticker]

    return result


def run_hypothetical_stress_tests(
    exposure_history: pd.DataFrame,
) -> pd.DataFrame:
    """Run every hypothetical stress scenario."""

    latest_portfolio = exposure_history.iloc[-1]

    current_values = pd.Series(
        {
            ticker: latest_portfolio[f"{ticker}_value"]
            for ticker in TICKERS
        }
    )

    results = []

    for scenario_name, shocks in STRESS_SCENARIOS.items():
        result = calculate_stress_scenario(
            current_values,
            scenario_name,
            shocks,
        )

        results.append(result)

    return pd.DataFrame(results).set_index("scenario")


def save_results(stress_results: pd.DataFrame) -> None:
    """Save the hypothetical stress-test results."""

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    stress_results.to_csv(OUTPUT_PATH)


if __name__ == "__main__":
    exposure_history = load_portfolio_exposure()

    stress_results = run_hypothetical_stress_tests(
        exposure_history
    )

    save_results(stress_results)

    print("Hypothetical stress tests completed successfully.")

    for scenario, result in stress_results.iterrows():
        print(f"\n{scenario}")

        print(
            f"Portfolio return: "
            f"{result['portfolio_return']:.2%}"
        )

        print(
            f"Portfolio P&L: "
            f"${result['portfolio_pnl']:,.2f}"
        )

        print(
            f"Stressed portfolio value: "
            f"${result['stressed_portfolio_value']:,.2f}"
        )