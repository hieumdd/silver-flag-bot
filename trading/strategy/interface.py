from abc import ABCMeta, abstractmethod
import io
from itertools import chain
from typing import Optional

import pandas as pd

from data.provider import DataProvider
from trading.signal.enum import LongEntry, ShortEntry
from trading.signal.model import Signal


class Strategy(metaclass=ABCMeta):
    def __init__(self, symbol: str):
        self.symbol = symbol

    @property
    @abstractmethod
    def data_provider(cls) -> DataProvider:
        pass

    def get_data(self):
        return self.data_provider.get(self.symbol)

    @abstractmethod
    def populate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        pass

    def generate_indicators(self, df: Optional[pd.DataFrame] = None) -> pd.DataFrame:
        return self.populate_indicators(df if df is not None else self.get_data())

    @abstractmethod
    def populate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        pass

    def generate_signals(self, df: Optional[pd.DataFrame] = None) -> pd.DataFrame:
        return self.populate_signals(
            df if df is not None else self.generate_indicators()
        )

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

    def populate_plot(self, df: pd.DataFrame) -> Optional[io.BytesIO]:
        return None

    def generate_plot(self, df: Optional[pd.DataFrame] = None) -> Optional[io.BytesIO]:
        plotter = self.populate_plot(df if df is not None else self.generate_signals())

        if plotter is None:
            return None
        
        buffer = io.BytesIO()
        plotter(
            type="candle",
            tight_layout=True,
            volume=True,
            figratio=(16, 10),
            style="charles",
            savefig=buffer,
        )
        buffer.seek(0)
        return buffer
