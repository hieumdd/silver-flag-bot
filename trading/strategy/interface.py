from abc import ABCMeta, abstractmethod
import io
from typing import Optional

import pandas as pd
import mplfinance as mpf

from data.provider import DataProvider
from trading.signal.model import Analysis, Signal, LongEntry, ShortEntry


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
    ) -> tuple[Analysis, Optional[Signal]]:
        _df = df if df is not None else self.generate_signals()

        latest_candle = _df.iloc[-1, :]

        def _parse_signal() -> Optional[Signal]:
            long_entry = latest_candle[LongEntry.flag_col] == True
            short_entry = latest_candle[ShortEntry.flag_col] == True

            if long_entry and not short_entry:
                return Signal(LongEntry, str(latest_candle["close"]))

            if short_entry and not long_entry:
                return Signal(ShortEntry, str(latest_candle["close"]))

            return None

        return (
            Analysis(
                strategy=str(type(self).__name__),
                symbol=self.symbol,
                timestamp=latest_candle.index.name,
                plot=self.generate_plot(_df),
            ),
            _parse_signal(),
        )
