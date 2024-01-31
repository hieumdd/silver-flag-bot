from abc import ABCMeta, abstractmethod
import io
from itertools import chain
from typing import Optional

import pandas as pd
import mplfinance as mpf

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

    def populate_subplots(self, df: pd.DataFrame) -> list[dict]:
        return []

    def generate_plot(self, df: Optional[pd.DataFrame] = None) -> io.BytesIO:
        _df = (df if df is not None else self.generate_signals()).iloc[-90:]

        buffer = io.BytesIO()
        mpf.plot(
            _df,
            type="candle",
            tight_layout=True,
            volume=True,
            figratio=(16, 10),
            style="charles",
            addplot=self.populate_subplots(_df),
            savefig=buffer,
        )
        buffer.seek(0)

        return buffer

    def analyze(
        self,
        df: Optional[pd.DataFrame] = None,
    ) -> tuple[io.BytesIO, list[Signal]]:
        _df = df if df is not None else self.generate_signals()

        plot = self.generate_plot(_df)

        current_candle = _df.iloc[-1, :]
        signals = list(
            chain(
                *[
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
            )
        )

        return (plot, signals)
