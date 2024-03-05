from abc import ABCMeta, abstractmethod
from functools import partial
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
        df = self.generate_indicators().copy()
        df.loc[:, [LongEntry.flag_col, ShortEntry.flag_col]] = (False, False)
        return self.populate_signals(df)

    def populate_subplots(self, df: pd.DataFrame) -> list[dict]:
        return []

    def create_plot(self, _df: pd.DataFrame, candles: int):
        df = _df.iloc[-candles:].copy()
        indicator_subplots = self.populate_subplots(df)

        signal_plot = partial(
            mpf.make_addplot,
            type="scatter",
            panel=0,
            markersize=200,
        )

        long_entry = df[LongEntry.flag_col] == True
        df.loc[long_entry, LongEntry.marker_col] = df.loc[long_entry, "high"]
        long_signal_plot = (
            []
            if df[LongEntry.marker_col].isna().all()
            else [signal_plot(df[LongEntry.marker_col], marker="^", color="lime")]
        )

        short_entry = df[ShortEntry.flag_col] == True
        df.loc[short_entry, ShortEntry.marker_col] = df.loc[short_entry, "low"]
        short_signal_plot = (
            []
            if df[ShortEntry.marker_col].isna().all()
            else [signal_plot(df[ShortEntry.marker_col], marker="v", color="pink")]
        )

        plot = io.BytesIO()
        mpf.plot(
            df,
            type="candle",
            tight_layout=True,
            volume=True,
            figratio=(16, 10),
            style="tradingview",
            addplot=[*indicator_subplots, *long_signal_plot, *short_signal_plot],
            savefig=plot,
        )
        plot.seek(0)
        return plot

    def analyze(self, candles: Optional[int] = 90) -> tuple[Analysis, Optional[Signal]]:
        df = self.generate_signals().iloc[-candles:]

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
                plot=self.create_plot(df),
            ),
            create_signal(),
        )
