from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_ROOT / "data" / "processed"
PLOT_PATH = PROJECT_ROOT / "plots"

RISK_PATH = DATA_PATH / "var_backtest.csv"
EXPOSURE_PATH = DATA_PATH / "portfolio_exposure.csv"

HISTORICAL_STRESS_PATH = (
    DATA_PATH / "historical_stress_tests.csv"
)

HYPOTHETICAL_STRESS_PATH = (
    DATA_PATH / "hypothetical_stress_tests.csv"
)


def load_data():
    """Load all datasets required for the plots."""

    risk_data = pd.read_csv(
        RISK_PATH,
        parse_dates=["date"],
        index_col="date",
    )

    exposure_data = pd.read_csv(
        EXPOSURE_PATH,
        parse_dates=["date"],
        index_col="date",
    )

    historical_stress = pd.read_csv(
        HISTORICAL_STRESS_PATH,
        index_col="scenario",
    )

    hypothetical_stress = pd.read_csv(
        HYPOTHETICAL_STRESS_PATH,
        index_col="scenario",
    )

    return (
        risk_data,
        exposure_data,
        historical_stress,
        hypothetical_stress,
    )


def plot_portfolio_performance(
    risk_data: pd.DataFrame,
) -> None:
    """Plot portfolio value and drawdown over time."""

    figure, axes = plt.subplots(
        2,
        1,
        figsize=(12, 8),
        sharex=True,
    )

    axes[0].plot(
        risk_data.index,
        risk_data["portfolio_value"],
        color="navy",
    )

    axes[0].set_title("Portfolio Value Over Time")
    axes[0].set_ylabel("Portfolio value ($)")
    axes[0].grid(alpha=0.3)

    axes[1].plot(
        risk_data.index,
        risk_data["drawdown"] * 100,
        color="darkred",
    )

    axes[1].fill_between(
        risk_data.index,
        risk_data["drawdown"] * 100,
        0,
        color="red",
        alpha=0.2,
    )

    axes[1].set_title("Portfolio Drawdown")
    axes[1].set_ylabel("Drawdown (%)")
    axes[1].set_xlabel("Date")
    axes[1].grid(alpha=0.3)

    figure.tight_layout()

    figure.savefig(
        PLOT_PATH / "portfolio_performance.png",
        dpi=300,
        bbox_inches="tight",
    )

    plt.close(figure)


def plot_var_backtest(
    risk_data: pd.DataFrame,
) -> None:
    """Plot actual portfolio losses against historical VaR."""

    chart_data = risk_data.dropna(
        subset=[
            "actual_loss_return",
            "var_95_return",
        ]
    ).tail(500)

    actual_losses = (
        chart_data["actual_loss_return"]
        .clip(lower=0)
        * 100
    )

    var_threshold = chart_data["var_95_return"] * 100

    exceptions = (
        chart_data["var_exception"]
        .astype(str)
        .str.lower()
        .eq("true")
    )

    figure, axis = plt.subplots(figsize=(12, 6))

    axis.plot(
        chart_data.index,
        actual_losses,
        color="steelblue",
        alpha=0.6,
        label="Actual daily loss",
    )

    axis.plot(
        chart_data.index,
        var_threshold,
        color="darkorange",
        linewidth=2,
        label="95% VaR threshold",
    )

    axis.scatter(
        chart_data.index[exceptions],
        actual_losses[exceptions],
        color="red",
        label="VaR exception",
        zorder=3,
    )

    axis.set_title(
        "Actual Portfolio Losses Compared with 95% VaR"
    )

    axis.set_ylabel("Loss (%)")
    axis.set_xlabel("Date")
    axis.legend()
    axis.grid(alpha=0.3)

    figure.tight_layout()

    figure.savefig(
        PLOT_PATH / "var_backtest.png",
        dpi=300,
        bbox_inches="tight",
    )

    plt.close(figure)


def plot_current_exposure(
    exposure_data: pd.DataFrame,
) -> None:
    """Plot the latest percentage exposure to every ETF."""

    exposure_columns = [
        column
        for column in exposure_data.columns
        if column.endswith("_exposure")
    ]

    latest_exposure = (
        exposure_data[exposure_columns]
        .iloc[-1]
        .rename(
            lambda name: name.replace("_exposure", "")
        )
        * 100
    )

    latest_exposure = latest_exposure.sort_values()

    figure, axis = plt.subplots(figsize=(9, 5))

    latest_exposure.plot(
        kind="barh",
        ax=axis,
        color="mediumseagreen",
    )

    axis.set_title("Current Portfolio Exposure")
    axis.set_xlabel("Portfolio exposure (%)")
    axis.set_ylabel("ETF")
    axis.grid(axis="x", alpha=0.3)

    figure.tight_layout()

    figure.savefig(
        PLOT_PATH / "current_exposure.png",
        dpi=300,
        bbox_inches="tight",
    )

    plt.close(figure)


def plot_stress_tests(
    historical_stress: pd.DataFrame,
    hypothetical_stress: pd.DataFrame,
) -> None:
    """Plot historical and hypothetical stress-test returns."""

    historical_returns = (
        historical_stress["total_return"]
        .sort_values()
        * 100
    )

    hypothetical_returns = (
        hypothetical_stress["portfolio_return"]
        .sort_values()
        * 100
    )

    figure, axes = plt.subplots(
        1,
        2,
        figsize=(14, 6),
    )

    historical_returns.plot(
        kind="barh",
        ax=axes[0],
        color="indianred",
    )

    axes[0].set_title("Historical Stress Tests")
    axes[0].set_xlabel("Portfolio return (%)")
    axes[0].set_ylabel("")
    axes[0].grid(axis="x", alpha=0.3)

    hypothetical_returns.plot(
        kind="barh",
        ax=axes[1],
        color="darkorange",
    )

    axes[1].set_title("Hypothetical Stress Tests")
    axes[1].set_xlabel("Portfolio return (%)")
    axes[1].set_ylabel("")
    axes[1].grid(axis="x", alpha=0.3)

    figure.tight_layout()

    figure.savefig(
        PLOT_PATH / "stress_tests.png",
        dpi=300,
        bbox_inches="tight",
    )

    plt.close(figure)


if __name__ == "__main__":
    PLOT_PATH.mkdir(parents=True, exist_ok=True)

    (
        risk_data,
        exposure_data,
        historical_stress,
        hypothetical_stress,
    ) = load_data()

    plot_portfolio_performance(risk_data)
    plot_var_backtest(risk_data)
    plot_current_exposure(exposure_data)

    plot_stress_tests(
        historical_stress,
        hypothetical_stress,
    )

    print("Plots created successfully.")
    print(f"Saved to: {PLOT_PATH}")