from abc import ABCMeta, abstractmethod
from functools import partial
import io
from typing import Optional

import numpy as np
import pandas as pd
import mplfinance as mpf

from logger import get_logger
from trading.data import DataProvider
from trading.signal import Analysis, Signal, Long, Short


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
        df.loc[:, [Long.value_col, Short.value_col]] = (np.nan, np.nan)
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

        long_marker = f"{Long.tag}Marker"
        df[long_marker] = np.nan
        df.loc[df[Long.value_col].notnull(), long_marker] = df["high"]
        long_signal_plot = (
            []
            if df[Long.value_col].isna().all()
            else [signal_plot(df[long_marker] + 0.3, marker=10, color="mediumseagreen")]
        )

        short_marker = f"{Short.tag}Marker"
        df[short_marker] = np.nan
        df.loc[df[Short.value_col].notnull(), short_marker] = df["low"]
        short_signal_plot = (
            []
            if df[Short.value_col].isna().all()
            else [signal_plot(df[short_marker] - 0.3, marker=11, color="lightcoral")]
        )

        plot = io.BytesIO()
        mpf.plot(
            df,
            type="candle",
            volume=True,
            figratio=(16, 10),
            style="tradingview",
            addplot=[*indicator_subplots, *long_signal_plot, *short_signal_plot],
            savefig=plot,
        )
        plot.seek(0)
        return plot

    def create_signal(self, df: pd.DataFrame) -> Optional[Signal]:
        candle = df.loc[df.index < self.data_provider.timeframe.is_finished()].iloc[-1]
        logger.debug(
            f"[O] {candle['open']} [H] {candle['high']} [L] {candle['low']} [C] {candle['close']}",
            extra={"candle": candle.to_dict()},
        )

        long_entry = candle[Long.value_col] != np.nan
        short_entry = candle[Short.value_col] != np.nan

        signal = None
        if long_entry and not short_entry:
            signal = Signal(Long, str(candle[Long.value_col]))
        elif short_entry and not long_entry:
            signal = Signal(Short, str(candle[Short.value_col]))

        return signal

    def analyze(self, candles: Optional[int] = 90) -> tuple[Analysis, Optional[Signal]]:
        df = self.generate_signals()

        plot = self.create_plot(df, candles)
        signal = self.create_signal(df)

        return (
            Analysis(
                strategy=str(type(self).__name__),
                symbol=self.symbol,
                timestamp=df.index[-1].to_pydatetime().isoformat(),
                plot=plot,
            ),
            signal,
        )
