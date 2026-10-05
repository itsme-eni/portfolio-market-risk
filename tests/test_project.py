import numpy as np
import pandas as pd

from src.build_portfolio import (
    INITIAL_PORTFOLIO_VALUE,
    WEIGHTS,
    build_portfolio_history,
    calculate_holdings,
)
from src.calculate_risk_metrics import calculate_drawdown
from src.calculate_var_es import calculate_expected_shortfall


def test_weights_add_up_to_one():
    """The portfolio must invest exactly 100% of its money."""

    assert np.isclose(sum(WEIGHTS.values()), 1.0)


def test_initial_portfolio_value():
    """The portfolio must begin with the configured initial value."""

    prices = pd.DataFrame(
        {
            "SPY": [100.0, 110.0],
            "QQQ": [100.0, 110.0],
            "AGG": [100.0, 110.0],
            "GLD": [100.0, 110.0],
            "EEM": [100.0, 110.0],
        },
        index=pd.to_datetime(["2026-01-01", "2026-01-02"]),
    )

    shares = calculate_holdings(prices)
    history = build_portfolio_history(prices, shares)

    assert np.isclose(
        history["portfolio_value"].iloc[0],
        INITIAL_PORTFOLIO_VALUE,
    )


def test_drawdown_calculation():
    """A decline from 120 to 90 should produce a 25% drawdown."""

    portfolio_history = pd.DataFrame(
        {"portfolio_value": [100.0, 120.0, 90.0]}
    )

    result = calculate_drawdown(portfolio_history)

    assert np.isclose(result["running_peak"].iloc[-1], 120.0)
    assert np.isclose(result["drawdown"].iloc[-1], -0.25)


def test_expected_shortfall_is_at_least_var():
    """Expected Shortfall should be at least as severe as VaR."""

    losses = np.array(
        [0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.10]
    )

    var = np.quantile(losses, 0.95)
    expected_shortfall = calculate_expected_shortfall(losses)

    assert expected_shortfall >= var