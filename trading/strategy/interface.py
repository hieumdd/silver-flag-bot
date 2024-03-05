from abc import ABCMeta, abstractmethod
import io
from typing import Optional

import pandas as pd
import mplfinance as mpf

from logger import get_logger
from trading.data import DataProvider
from trading.signal.model import Analysis, Signal, LongEntry, ShortEntry


logger = get_logger(__name__)


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

    def generate_indicators(self) -> pd.DataFrame:
        return self.populate_indicators(self.get_data().copy())

    @abstractmethod
    def populate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        pass

    def generate_signals(self) -> pd.DataFrame:
        return self.populate_signals(self.generate_indicators().copy())

    def populate_subplots(self, df: pd.DataFrame) -> list[dict]:
        return []

    def analyze(self, candles: Optional[int] = 90) -> tuple[Analysis, Optional[Signal]]:
        df = self.generate_signals().iloc[-candles:]

        def create_plot():
            plot = io.BytesIO()
            mpf.plot(
                df,
                type="candle",
                tight_layout=True,
                volume=True,
                figratio=(16, 10),
                style="tradingview",
                addplot=self.populate_subplots(df),
                savefig=plot,
            )
            plot.seek(0)
            return plot

        latest_candle = df.iloc[-1, :]
        logger.debug("Latest candle", extra={"latest_candle": latest_candle.to_dict()})

        def create_signal() -> Optional[Signal]:
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
                timestamp=latest_candle.name.to_pydatetime().isoformat(),
                plot=create_plot(),
            ),
            create_signal(),
        )
