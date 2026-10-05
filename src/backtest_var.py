from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]

INPUT_PATH = PROJECT_ROOT / "data" / "processed" / "var_es_metrics.csv"
OUTPUT_PATH = PROJECT_ROOT / "data" / "processed" / "var_backtest.csv"

CONFIDENCE_LEVEL = 0.95
ROLLING_WINDOW = 252


def load_var_metrics() -> pd.DataFrame:
    """Load the portfolio returns and historical VaR estimates."""

    return pd.read_csv(
        INPUT_PATH,
        parse_dates=["date"],
        index_col="date",
    )


def backtest_var(var_metrics: pd.DataFrame) -> pd.DataFrame:
    """Compare actual portfolio losses with previous VaR estimates."""

    backtest_results = var_metrics.copy()

    # Convert negative returns into positive losses.
    backtest_results["actual_loss_return"] = (
        -backtest_results["daily_return"]
    )

    valid_var = backtest_results["var_95_return"].notna()

    backtest_results["var_exception"] = pd.Series(
        pd.NA,
        index=backtest_results.index,
        dtype="boolean",
    )

    backtest_results.loc[valid_var, "var_exception"] = (
        backtest_results.loc[valid_var, "actual_loss_return"]
        > backtest_results.loc[valid_var, "var_95_return"]
    )

    backtest_results["rolling_exception_rate"] = (
        backtest_results["var_exception"]
        .astype("Float64")
        .rolling(
            window=ROLLING_WINDOW,
            min_periods=1,
        )
        .mean()
    )

    return backtest_results


def save_backtest(backtest_results: pd.DataFrame) -> None:
    """Save the VaR backtesting results."""

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    backtest_results.to_csv(OUTPUT_PATH)


if __name__ == "__main__":
    var_metrics = load_var_metrics()
    backtest_results = backtest_var(var_metrics)
    save_backtest(backtest_results)

    evaluated_days = backtest_results.dropna(
        subset=["var_exception"]
    )

    number_of_days = len(evaluated_days)
    exception_count = int(evaluated_days["var_exception"].sum())

    observed_exception_rate = exception_count / number_of_days
    expected_exception_rate = 1 - CONFIDENCE_LEVEL
    expected_exception_count = number_of_days * expected_exception_rate

    print("VaR backtesting completed successfully.")

    print(f"\nEvaluated days: {number_of_days}")
    print(f"Observed exceptions: {exception_count}")
    print(f"Expected exceptions: {expected_exception_count:.1f}")

    print(
        f"Observed exception rate: {observed_exception_rate:.2%}"
    )
    print(
        f"Expected exception rate: {expected_exception_rate:.2%}"
    )