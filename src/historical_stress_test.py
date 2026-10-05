from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]

INPUT_PATH = PROJECT_ROOT / "data" / "processed" / "portfolio_history.csv"
OUTPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "historical_stress_tests.csv"
)

STRESS_SCENARIOS = {
    "2018 market sell-off": ("2018-09-20", "2018-12-24"),
    "COVID-19 crash": ("2020-02-19", "2020-03-23"),
    "2022 market decline": ("2022-01-03", "2022-10-14"),
}


def load_portfolio_history() -> pd.DataFrame:
    """Load the simulated portfolio history."""

    return pd.read_csv(
        INPUT_PATH,
        parse_dates=["date"],
        index_col="date",
    )


def analyse_stress_period(
    portfolio_history: pd.DataFrame,
    scenario_name: str,
    start_date: str,
    end_date: str,
) -> dict:
    """Calculate portfolio performance during one stress period."""

    stress_period = portfolio_history.loc[start_date:end_date].copy()

    if stress_period.empty:
        raise ValueError(
            f"No portfolio data found for {scenario_name}."
        )

    starting_value = stress_period["portfolio_value"].iloc[0]
    ending_value = stress_period["portfolio_value"].iloc[-1]

    total_pnl = ending_value - starting_value
    total_return = ending_value / starting_value - 1

    running_peak = stress_period["portfolio_value"].cummax()

    stress_drawdown = (
        stress_period["portfolio_value"] / running_peak - 1
    )

    maximum_drawdown = stress_drawdown.min()
    worst_daily_return = stress_period["daily_return"].min()
    worst_daily_pnl = stress_period["daily_pnl"].min()

    return {
        "scenario": scenario_name,
        "start_date": stress_period.index.min(),
        "end_date": stress_period.index.max(),
        "starting_value": starting_value,
        "ending_value": ending_value,
        "total_pnl": total_pnl,
        "total_return": total_return,
        "maximum_drawdown": maximum_drawdown,
        "worst_daily_return": worst_daily_return,
        "worst_daily_pnl": worst_daily_pnl,
    }


def run_historical_stress_tests(
    portfolio_history: pd.DataFrame,
) -> pd.DataFrame:
    """Run all historical stress scenarios."""

    results = []

    for scenario_name, dates in STRESS_SCENARIOS.items():
        start_date, end_date = dates

        result = analyse_stress_period(
            portfolio_history,
            scenario_name,
            start_date,
            end_date,
        )

        results.append(result)

    return pd.DataFrame(results).set_index("scenario")


def save_results(stress_results: pd.DataFrame) -> None:
    """Save the historical stress-test results."""

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    stress_results.to_csv(OUTPUT_PATH)


if __name__ == "__main__":
    portfolio_history = load_portfolio_history()

    stress_results = run_historical_stress_tests(
        portfolio_history
    )

    save_results(stress_results)

    print("Historical stress tests completed successfully.")

    for scenario, result in stress_results.iterrows():
        print(f"\n{scenario}")
        print(f"Total return: {result['total_return']:.2%}")
        print(f"Total P&L: ${result['total_pnl']:,.2f}")
        print(
            f"Maximum drawdown: "
            f"{result['maximum_drawdown']:.2%}"
        )
        print(
            f"Worst daily return: "
            f"{result['worst_daily_return']:.2%}"
        )