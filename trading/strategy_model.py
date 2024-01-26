from abc import ABCMeta, abstractmethod
from datetime import datetime

import numpy as np
import pandas as pd
import pandas_ta as ta

from ssi.client_model import GetIntradayOptions
from ssi.client_service import SSIClient


class Strategy(metaclass=ABCMeta):
    def get_data(self):
        df = pd.DataFrame(SSIClient().get_intraday(self.get_options()))

        def clean():
            def create_timestamp(row):
                _date = datetime.strptime(row["TradingDate"], "%d/%m/%Y").date()
                _time = datetime.strptime(row["Time"], "%H:%M:%S").time()
                return datetime.combine(_date, _time)

            _df = df.copy().drop_duplicates()
            _df = _df.set_index(pd.DatetimeIndex(_df.apply(create_timestamp, axis=1)))
            _df = _df.drop(columns=["TradingDate", "Time"])
            for col_name in ["Value", "Open", "High", "Low", "Close"]:
                _df[col_name] = _df[col_name].astype(float)
            _df = _df.rename(str.lower, axis="columns")
            _df = _df.sort_index()

            return _df

        return clean()

    @abstractmethod
    def get_options(self) -> GetIntradayOptions:
        pass

    @abstractmethod
    def populate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        pass

    @abstractmethod
    def generate_signals(self, df: pd.DataFrame):
        pass


class MultiMA(Strategy):
    _range = range(5, 150, 5)

    def get_options(self):
        date_range = pd.bdate_range(end=datetime.today().date(), periods=7)
        return GetIntradayOptions(
            symbol="VN30F1M",
            start_date=date_range[0].to_pydatetime(),
            end_date=date_range[-1].to_pydatetime(),
        )

    def populate_indicators(self, df: pd.DataFrame):
        _df = df.copy()
        for length in self._range:
            _df[f"EMA_{length}"] = ta.ema(_df["close"], length=length)
            _df[f"EMA_{length}_FLAG"] = np.where(
                _df["close"] > _df[f"EMA_{length}"], 1, -1
            )
        return _df

    def generate_signals(self, df: pd.DataFrame):
        pass
