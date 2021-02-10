from typing import Any, List, Optional, Union, Dict

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin

from skbonus.exceptions import NoFrequencyError


class SimpleTimeFeatures(BaseEstimator, TransformerMixin):
    """
    This class enriches pandas dataframes with a DatetimeIndex with new columns. These new columns are easy
    derivations from the index, such as the day of week or month.
    This is especially useful when dealing with time series regressions or classifications.

    Parameters
    ----------
    second : bool, default=False
        Whether to extract the day of week from the index and add it as a new column.

    minute : bool, default=False
        Whether to extract the day of week from the index and add it as a new column.

    hour : bool, default=False
        Whether to extract the day of week from the index and add it as a new column.

    day_of_week : bool, default=False
        Whether to extract the day of week from the index and add it as a new column.

    day_of_month : bool, default=False
        Whether to extract the day of month from the index and add it as a new column.

    day_of_year : bool, default=False
        Whether to extract the day of year from the index and add it as a new column.

    week_of_month : bool, default=False
        Whether to extract the week of month from the index and add it as a new column.

    week_of_year : bool, default=False
        Whether to extract the week of year from the index and add it as a new column.

    month : bool, default=False
        Whether to extract the month from the index and add it as a new column.

    year : bool, default=False
        Whether to extract the year from the index and add it as a new column.

    Examples
    --------
    >>> import pandas as pd
    >>> df = pd.DataFrame(
    ...     {"A": ["a", "b", "c"]},
    ...     index=[
    ...         pd.Timestamp("1988-08-08"),
    ...         pd.Timestamp("2000-01-01"),
    ...         pd.Timestamp("1950-12-31"),
    ...     ])
    >>> SimpleTimeFeatures(day_of_month=True, month=True, year=True).fit_transform(df)
                A   day_of_month    month    year
    1988-08-08  a              8        8    1988
    2000-01-01  b              1        1    2000
    1950-12-31  c             31       12    1950
    """

    def __init__(
        self,
        second: bool = False,
        minute: bool = False,
        hour: bool = False,
        day_of_week: bool = False,
        day_of_month: bool = False,
        day_of_year: bool = False,
        week_of_month: bool = False,
        week_of_year: bool = False,
        month: bool = False,
        year: bool = False,
    ) -> None:
        self.second = second
        self.minute = minute
        self.hour = hour
        self.day_of_week = day_of_week
        self.day_of_month = day_of_month
        self.day_of_year = day_of_year
        self.week_of_month = week_of_month
        self.week_of_year = week_of_year
        self.month = month
        self.year = year

    def _add_second(self, X: pd.DataFrame) -> pd.DataFrame:
        return X.assign(second=lambda df: df.index.second) if self.second else X

    def _add_minute(self, X: pd.DataFrame) -> pd.DataFrame:
        return X.assign(minute=lambda df: df.index.minute) if self.minute else X

    def _add_hour(self, X: pd.DataFrame) -> pd.DataFrame:
        return X.assign(hour=lambda df: df.index.hour) if self.hour else X

    def _add_day_of_week(self, X: pd.DataFrame) -> pd.DataFrame:
        return (
            X.assign(day_of_week=lambda df: df.index.weekday + 1)
            if self.day_of_week
            else X
        )

    def _add_day_of_month(self, X: pd.DataFrame) -> pd.DataFrame:
        return (
            X.assign(day_of_month=lambda df: df.index.day) if self.day_of_month else X
        )

    def _add_day_of_year(self, X: pd.DataFrame) -> pd.DataFrame:
        return (
            X.assign(day_of_year=lambda df: df.index.dayofyear)
            if self.day_of_year
            else X
        )

    def _add_week_of_month(self, X: pd.DataFrame) -> pd.DataFrame:
        return (
            X.assign(week_of_month=lambda df: np.ceil(df.index.day / 7).astype(int))
            if self.week_of_month
            else X
        )

    def _add_week_of_year(self, X: pd.DataFrame) -> pd.DataFrame:
        return (
            X.assign(week_of_year=lambda df: df.index.isocalendar().week)
            if self.week_of_year
            else X
        )

    def _add_month(self, X: pd.DataFrame) -> pd.DataFrame:
        return X.assign(month=lambda df: df.index.month) if self.month else X

    def _add_year(self, X: pd.DataFrame) -> pd.DataFrame:
        return X.assign(year=lambda df: df.index.year) if self.year else X

    def fit(self, X: pd.DataFrame, y: Any = None) -> "SimpleTimeFeatures":
        """
        Fit the estimator. In this special case, nothing is done.

        Parameters
        ----------
        X : pd.DataFrame
            A pandas dataframe with a DatetimeIndex.

        y : Ignored
            Not used, present here for API consistency by convention.

        Returns
        -------
        self
            Fitted transformer.
        """
        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """
        Inserts all chosen time features as new columns into the dataframe and outputs it.

        Parameters
        ----------
        X : pd.DataFrame
            A pandas dataframe with a DatetimeIndex.

        Returns
        -------
        transformed_X : pd.DataFrame
            A pandas dataframe with additional time feature columns.
        """
        res = (
            X.pipe(self._add_day_of_week)
            .pipe(self._add_second)
            .pipe(self._add_minute)
            .pipe(self._add_hour)
            .pipe(self._add_day_of_month)
            .pipe(self._add_day_of_year)
            .pipe(self._add_week_of_month)
            .pipe(self._add_week_of_year)
            .pipe(self._add_month)
            .pipe(self._add_year)
        )
        return res


class PowerTrend(BaseEstimator, TransformerMixin):
    """
    Adds a power trend to a pandas dataframe with a continous DatetimeIndex. For example, it can create a new column
    with numbers increasing quadratically in the index.

    Parameters
    ----------
    power : float
        Exponent to use for the trend, i.e. linear (power=1), root (power=0.5), or cube (power=3).

    Examples
    --------
    >>> import pandas as pd
    >>> df = pd.DataFrame(
    ...     {"A": ["a", "b", "c", "d"]},
    ...     index=pd.date_range(start="1988-08-08", periods=4)
    ... )
    >>> PowerTrend(power=2).fit_transform(df)
                A   trend
    1988-08-08  a     0.0
    1988-08-09  b     1.0
    1988-08-10  c     4.0
    1988-08-11  d     9.0
    """

    def __init__(self, power: float = 1) -> None:
        self.power = power

    def fit(self, X: pd.DataFrame, y: None = None) -> "PowerTrend":
        """
        Fits the model. It assigns value 0 to the first item of the time index and 1 to the second one etc.
        This way, we can get a value for any other date in a linear fashion. These values are later transformed.

        Raises a NoFrequencyError if the DatetimeIndex has no frequency. This happens, for example, if you don't use a
        TimeSeriesSplit when using cross validation.

        Parameters
        ----------
        X : pd.DataFrame
            A pandas dataframe with a DatetimeIndex.

        y : Ignored
            Not used, present here for API consistency by convention.

        Returns
        -------
        self
            Fitted transformer.
        """
        self.freq_ = X.index.freq
        if self.freq_ is None:
            raise NoFrequencyError(
                "DatetimeIndex has no frequency. This can happen when doing cross validation without using a TimeSeriesSplit."
            )
        self.t0 = X.index.min()

        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """
        Add the trend column to the input dataframe.

        Parameters
        ----------
        X : pd.DataFrame
             A pandas dataframe with a DatetimeIndex.

        Returns
        -------
        transformed_X : pd.DataFrame
            The dataframe with an additional trend column.

        """
        index_as_int = (X.index - self.t0) / self.freq_
        return X.assign(trend=index_as_int ** self.power)


class SpecialDayBumps(BaseEstimator, TransformerMixin):
    """
    This class enriches pandas dataframes with a DatetimeIndex with new columns. These new columns
    contain whether the index lies within a time interval. For example, the output can be
    a one hot encoded column containing a 1 if the corresponding date from the index is within
    the given date range, and 0 otherwise.
    The output can also be a smoothed via a general Gaussian sliding window over the one hot encoded column as
    a next step. This makes sense when, for example, a certain holiday has effects on the next days or the days
    before, too. See the examples to get a better understanding.

    This is especially useful when dealing with time series regressions or classifications.

    Parameters
    ----------
    name : str
        The name of the new column. Usually a holiday name such as Easter, Christmas, Black Friday, ...

    dates : List[Union[pd.Timestamp, str]]
        A list containing the dates of the holiday. You have to state every holiday explicitly, i.e.
        Christmas from 2018 to 2020 can be encoded as ["2018-12-24", "2019-12-24", "2020-12-24"].

    window : int, default=1
        Size of the sliding window. Used for smoothing the simple one hot encoded output. Increasing
        it to something larger than 1 only makes sense for a DatetimeIndex with equidistant dates.

    win_type : Optional[str], default=None
        Type of smoothing. A value of None leaves the default one hot encoding, i.e. the output column
        contains 0 and 1 only. Another interesting window is "general_gaussian", which also requires the parameters
        p and sig. See the notes below for further information.

    p : float, default=1
        Only used if win_type="general_gaussian". Determines the shape of the rolling curve. p=1 yields a typical
        Gaussian curve while p=0.5 yields a Laplace curve, for example.

    sig : float, default=1
        Only used if win_type="general_gaussian". Determines the standard deviation of the rolling curve.

    pad_value : Union[float, np.nan], default=0
        When using sliding windows of length > 1, the time series has to be extended to prevent NaNs at
        the start or end of the smoothed time series. If you wish for these NaNs, pad_value=input np.nan.
        See the examples below for further information.

    Examples
    --------
    >>> import pandas as pd
    >>> df = pd.DataFrame({"A": range(7)}, index=pd.date_range(start="2019-12-29", periods=7))
    >>> SpecialDayBumps("new_year_2020", ["2020-01-01"]).fit_transform(df)
                A   new_year_2020
    2019-12-29  0             0.0
    2019-12-30  1             0.0
    2019-12-31  2             0.0
    2020-01-01  3             1.0
    2020-01-02  4             0.0
    2020-01-03  5             0.0
    2020-01-04  6             0.0

    >>> SpecialDayBumps("new_year_2020", ["2020-01-01"],
    ... window=5, win_type="general_gaussian", p=1, sig=1).fit_transform(df)
                A   new_year_2020
    2019-12-29  0        0.000000
    2019-12-30  1        0.135335
    2019-12-31  2        0.606531
    2020-01-01  3        1.000000
    2020-01-02  4        0.606531
    2020-01-03  5        0.135335
    2020-01-04  6        0.000000

    >>> SpecialDayBumps("new_year_2020", ["2020-01-01"],
    ... window=5, win_type="general_gaussian", pad_value=np.nan,
    ... p=1, sig=1).fit_transform(df)
                A   new_year_2020
    2019-12-29  0             NaN
    2019-12-30  1             NaN
    2019-12-31  2        0.606531
    2020-01-01  3        1.000000
    2020-01-02  4        0.606531
    2020-01-03  5             NaN
    2020-01-04  6             NaN
    """

    def __init__(
        self,
        name: str,
        dates: List[Union[pd.Timestamp, str]],
        window: int = 1,
        win_type: Optional[str] = None,
        p: float = 1,
        sig: float = 1,
        pad_value: Union[float, "np.nan"] = 0,
    ) -> None:
        self.name = name
        self.dates = dates
        self.window = window
        self.win_type = win_type
        self.p = p
        self.sig = sig
        self.pad_value = pad_value

    def fit(self, X: pd.DataFrame, y: None = None) -> "SpecialDayBumps":
        """
        Fit the estimator. The frequency of the DatetimeIndex is extracted.

        Raises a NoFrequencyError if the DatetimeIndex has no frequency. This happens, for example, if you don't use a
        TimeSeriesSplit when using cross validation.

        Parameters
        ----------
        X : pd.DataFrame
            A pandas dataframe with a DatetimeIndex.

        y : Ignored
            Not used, present here for API consistency by convention.

        Returns
        -------
        self
            Fitted transformer.
        """
        self.freq_ = X.index.freq
        if self.freq_ is None:
            raise NoFrequencyError(
                "DatetimeIndex has no frequency. This can happen when doing cross validation without using a TimeSeriesSplit."
            )
        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """
        Adds the new date feature to the dataframe.

        Parameters
        ----------
        X : pd.DataFrame
            A pandas dataframe with a DatetimeIndex.

        Returns
        -------
        transformed_X : pd.DataFrame
            A pandas dataframe with an additional column for special dates.
        """
        dummy_dates = pd.Series(X.index.isin(self.dates), index=X.index)
        extended_index = extended_index = X.index.union(
            [X.index.min() - i * self.freq_ for i in range(1, self.window + 1)]
        ).union([X.index.max() + i * self.freq_ for i in range(1, self.window + 1)])

        smoothed_dates = (
            dummy_dates.reindex(extended_index)
            .fillna(self.pad_value)
            .rolling(window=self.window, center=True, win_type=self.win_type)
            .sum(p=self.p, sig=self.sig)
            .reindex(X.index)
            .values
        )

        return X.assign(**{self.name: smoothed_dates})


class CyclicalEncoder(BaseEstimator, TransformerMixin):
    """
    This class breaks each cyclic feature into two new features, corresponding to the representation of
    this feature on a circle. For example, take the hours from 0 to 23. On a normal, round  analog clock,
    these features are perfectly aligned on a circle already. You can do the same with days, month, ...

    The column names affected by default are
        - second
        - minute
        - hour
        - day_of_week
        - day_of_month
        - day_of_year
        - week_of_month
        - week_of_year
        - month

    You can add more with the additional_cycles parameter.

    This method has the advantage that close points in time stay close together. See the examples below.

    Otherwise, if algorithms deal with the raw value for hour they cannot know that 0 and 23 are actually close.
    Another possibility is one hot encoding the hour. This has the disadvantage that it breaks the distances
    between different hours. Hour 5 and 16 have the same distance as hour 0 and 23 when doing this.

    Parameters
    ----------
    additional_cycles : Optional[Dict[str, Dict[str, str]]], default=None
        Define additional additional_cycles in the form {cycle_name: {"min": min_value, "max": max_value}}, e.g.
        {"day_of_week": {"min": 1, "max": 7}}. Probably you need this only for very specific additional_cycles, as
        these ones are already implemented:
            - "second": {"min": 0, "max": 59},
            - "minute": {"min": 0, "max": 59},
            - "hour": {"min": 0, "max": 23},
            - "day_of_week": {"min": 1, "max": 7},
            - "day_of_month": {"min": 1, "max": 31},
            - "day_of_year": {"min": 1, "max": 366},
            - "week_of_month": {"min": 1, "max": 5},
            - "week_of_year": {"min": 1, "max": 53},
            - "month": {"min": 1, "max": 12}

    Examples
    --------
    >>> import pandas as pd
    >>> df = pd.DataFrame({"hour": [22, 23, 0, 1, 2]})
    >>> CyclicalEncoder().fit_transform(df)
        hour        hour_cos         hour_sin
    0     22        0.866025       -0.500000
    1     23        0.965926       -0.258819
    2      0        1.000000        0.000000
    3      1        0.965926        0.258819
    4      2        0.866025        0.500000
    """

    def __init__(
        self, additional_cycles: Optional[Dict[str, Dict[str, str]]] = None
    ) -> None:
        DEFAULT_CYCLES = {
            "second": {"min": 0, "max": 59},
            "minute": {"min": 0, "max": 59},
            "hour": {"min": 0, "max": 23},
            "day_of_week": {"min": 1, "max": 7},
            "day_of_month": {"min": 1, "max": 31},
            "day_of_year": {"min": 1, "max": 366},
            "week_of_month": {"min": 1, "max": 5},
            "week_of_year": {"min": 1, "max": 53},
            "month": {"min": 1, "max": 12},
        }
        self.additional_cycles = additional_cycles
        if additional_cycles is not None:
            self.additional_cycles.update(DEFAULT_CYCLES)
        else:
            self.additional_cycles = DEFAULT_CYCLES

    def fit(self, X: pd.DataFrame, y=None) -> "CyclicalEncoder":
        """
        Fit the estimator. In this special case, nothing is done.

        Parameters
        ----------
        X : pd.DataFrame
            A pandas dataframe with a DatetimeIndex.

        y : Ignored
            Not used, present here for API consistency by convention.

        Returns
        -------
        self
            Fitted transformer.
        """
        return self

    def transform(self, X):
        """
        Adds the cyclic features to the dataframe.

        Parameters
        ----------
        X : pd.DataFrame
            A pandas dataframe. The column names should be the one output by the SimpleTimeFeatures or
            as specified in the additional_cycles keyword in this class. The standard names are
                - "second"
                - "minute"
                - "hour"
                - "day_of_week"
                - "day_of_month"
                - "day_of_year"
                - "week_of_month"
                - "week_of_year"
                - "month"

        Returns
        -------
        transformed_X : pd.DataFrame
            A pandas dataframe with two additional columns for each original column.
        """
        return X.assign(
            **{
                f"{col}_cos": np.cos(
                    (X[col] - self.additional_cycles[col]["min"])
                    / (
                        self.additional_cycles[col]["max"]
                        + 1
                        - self.additional_cycles[col]["min"]
                    )
                    * 2
                    * np.pi
                )
                for col in X.columns.intersection(self.additional_cycles.keys())
            },
            **{
                f"{col}_sin": np.sin(
                    (X[col] - self.additional_cycles[col]["min"])
                    / (
                        self.additional_cycles[col]["max"]
                        + 1
                        - self.additional_cycles[col]["min"]
                    )
                    * 2
                    * np.pi
                )
                for col in X.columns.intersection(self.additional_cycles.keys())
            },
        )


if __name__ == "__main__":
    import doctest

    doctest.testmod(optionflags=doctest.NORMALIZE_WHITESPACE)
