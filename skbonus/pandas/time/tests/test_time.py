"""Test time classes."""

import numpy as np
import pandas as pd
import pytest

from skbonus.pandas.time import (
    PowerTrend,
    SimpleTimeFeatures,
    GeneralGaussianSmoother,
    DateIndicator,
)


@pytest.fixture
def get_non_continuous_data():
    """Generate data with a non-continuous DatetimeIndex."""
    return pd.DataFrame(
        {"A": ["a", "b", "c"], "B": [1, 2, 2], "C": [0, 1, 0]},
        index=[
            pd.Timestamp("1988-08-08 11:12:12"),
            pd.Timestamp("2000-01-01 07:06:05"),
            pd.Timestamp("1950-12-31"),
        ],
    )


@pytest.fixture
def get_continuous_data():
    """Generate data with a continuous DatetimeIndex."""
    return pd.DataFrame(
        {"data": range(60)}, index=pd.date_range(start="2018-11-01", periods=60)
    )


def test_simple_time_features_fit_transform(get_non_continuous_data):
    """Test SimpleTimeFeatures' fit and transform."""
    non_continuous_data = get_non_continuous_data

    dfa = SimpleTimeFeatures(
        second=True,
        minute=True,
        hour=True,
        day_of_week=True,
        day_of_month=True,
        day_of_year=True,
        week_of_month=True,
        week_of_year=True,
        month=True,
        year=True,
    )

    assert (
        (
            dfa.fit_transform(non_continuous_data)
            == pd.DataFrame(
                {
                    "A": ["a", "b", "c"],
                    "B": [1, 2, 2],
                    "C": [0, 1, 0],
                    "second": [12, 5, 0],
                    "minute": [12, 6, 0],
                    "hour": [11, 7, 0],
                    "day_of_week": [1, 6, 7],
                    "day_of_month": [8, 1, 31],
                    "day_of_year": [221, 1, 365],
                    "week_of_month": [2, 1, 5],
                    "week_of_year": [32, 52, 52],
                    "month": [8, 1, 12],
                    "year": [1988, 2000, 1950],
                },
                index=non_continuous_data.index,
            )
        )
        .all()
        .all()
    )


@pytest.mark.parametrize(
    "estimator",
    [
        GeneralGaussianSmoother(
            frequency="d",
            window=15,
            p=1,
            sig=1,
        ),
        GeneralGaussianSmoother(
            window=15,
            p=1,
            sig=1,
        ),
    ],
)
def test_special_day_bumps_fit_transform(get_continuous_data, estimator):
    """Test the SpecialDayBumps."""
    continuous_data = get_continuous_data
    d = DateIndicator("black_friday_2018", ["2018-11-23"])
    X = d.fit_transform(continuous_data)

    sda_transformed = estimator.fit_transform(X)

    np.testing.assert_almost_equal(
        sda_transformed.loc["2018-11-21":"2018-11-25", "black_friday_2018"].values,
        [0.053991, 0.2419707, 0.3989423, 0.2419707, 0.053991],
    )


def test_special_day_bumps_no_freq_error(get_non_continuous_data):
    """Test the SpecialDayBumps without frequency provided, and where it cannot be inferred during fit time."""
    non_continuous_data = get_non_continuous_data

    sda = GeneralGaussianSmoother(
        window=15,
        p=1,
        sig=1,
    )

    with pytest.raises(ValueError):
        sda.fit(non_continuous_data)


def test_power_trend_adder_fit_transform(get_continuous_data):
    """Test the PowerTrendAdder."""
    continuous_data = get_continuous_data
    pta = PowerTrend(frequency="d", origin_date="2018-11-01")

    assert pta.fit_transform(continuous_data).trend.tolist() == list(range(60))


def test_power_trend_adder_fit_transform_defaults(get_continuous_data):
    """Test the PowerTrendAdder without provided frequency and origin_date."""
    continuous_data = get_continuous_data
    pta = PowerTrend()

    assert pta.fit_transform(continuous_data).trend.tolist() == list(range(60))
    assert pta.freq_ == "D"
    assert pta.origin_ == pd.Timestamp("2018-11-01", freq="D")


def test_power_trend_adder_fit_transform_defaults_error(get_non_continuous_data):
    """Test the PowerTrendAdder without provided frequency and origin_date, and without the possibility to extract it during fit time."""
    non_continuous_data = get_non_continuous_data
    pta = PowerTrend()

    with pytest.raises(ValueError):
        pta.fit(non_continuous_data)
