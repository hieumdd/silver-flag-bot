from abc import ABCMeta, abstractmethod
from datetime import datetime
from typing import Optional

import pandas as pd

from ssi.client_model import GetIntradayOptions
from ssi.client_service import SSIClient


class Strategy(metaclass=ABCMeta):
    def get_data(self):
        def create_timestamp(row):
            return datetime.combine(
                datetime.strptime(row["TradingDate"], "%d/%m/%Y").date(),
                datetime.strptime(row["Time"], "%H:%M:%S").time(),
            )

        ohlc_columns = ["value", "open", "high", "low", "close"]

        df = pd.DataFrame(SSIClient().get_intraday(self.get_options()))

        df = (
            df.drop_duplicates()
            .set_index(pd.DatetimeIndex(df.apply(create_timestamp, axis=1)))
            .sort_index()
            .rename(str.lower, axis=1)
            .astype({col_name: float for col_name in ohlc_columns})
        )

        return df[ohlc_columns]

    @abstractmethod
    def get_options(self) -> GetIntradayOptions:
        pass

    @abstractmethod
    def populate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        pass

    def get_indicators(self, df: Optional[pd.DataFrame] = None) -> pd.DataFrame:
        return self.populate_indicators(df if df else self.get_data())

    @abstractmethod
    def populate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        pass

    def get_signals(self, df: Optional[pd.DataFrame] = None) -> pd.DataFrame:
        return self.populate_signals(df if df else self.get_indicators())
