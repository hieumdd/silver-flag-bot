from abc import ABCMeta, abstractmethod
from datetime import datetime
from itertools import chain
from typing import Optional

import pandas as pd

from ssi.options import GetIntradayOptions
from ssi.client import SSIClient
from trading.signal.enum import LongEntry, ShortEntry
from trading.signal.model import Signal


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

        return df[["symbol", *ohlc_columns]]

    @abstractmethod
    def get_options(self) -> GetIntradayOptions:
        pass

    @abstractmethod
    def populate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        pass

    def generate_indicators(self, df: Optional[pd.DataFrame] = None) -> pd.DataFrame:
        return self.populate_indicators(df if df else self.get_data())

    @abstractmethod
    def populate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        pass

    def generate_signals(self, df: Optional[pd.DataFrame] = None) -> pd.DataFrame:
        return self.populate_signals(df if df else self.generate_indicators())

    def get_signals(self, df: Optional[pd.DataFrame] = None):
        _df = df if df is not None else self.generate_signals()
        current_candle = _df.iloc[-1, :]
        signals = [
            [
                Signal(
                    type_,
                    current_candle["symbol"],
                    current_candle.name.to_pydatetime().isoformat(),
                    str(current_candle["close"]),
                    current_candle[type_.tag_col],
                )
            ]
            if current_candle[type_.flag_col] == True
            else []
            for type_ in [LongEntry, ShortEntry]
        ]
        return list(chain(*signals))
