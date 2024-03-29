from abc import ABCMeta, abstractmethod
from functools import partial
import io
from typing import Optional

import numpy as np
import pandas as pd
import mplfinance as mpf

from logger import get_logger
from trading.data import DataProvider
from trading.signal import Signal, Long, Short
from trading.analysis import Analysis


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
        df.loc[:, [Long.col, Short.col]] = (pd.NA, pd.NA)
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
        df.loc[df[Long.col].notnull(), long_marker] = df["high"]
        long_signal_plot = (
            []
            if df[Long.col].isna().all()
            else [signal_plot(df[long_marker] + 0.3, marker=10, color="mediumseagreen")]
        )

        short_marker = f"{Short.tag}Marker"
        df[short_marker] = np.nan
        df.loc[df[Short.col].notnull(), short_marker] = df["low"]
        short_signal_plot = (
            []
            if df[Short.col].isna().all()
            else [signal_plot(df[short_marker] - 0.3, marker=11, color="lightcoral")]
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
        df = self.generate_signals()

        candle = df.loc[df.index < self.data_provider.timeframe.is_finished()].iloc[-1]
        message = f"[O] {candle['open']} [H] {candle['high']} [L] {candle['low']} [C] {candle['close']}"
        logger.debug(message, extra={"candle": candle.to_dict()})

        long_entry = not pd.isna(candle[Long.col])
        short_entry = not pd.isna(candle[Short.col])

        signal = None
        if long_entry and not short_entry:
            signal = Signal(Long, self.symbol, str(candle[Long.col]))
        elif short_entry and not long_entry:
            signal = Signal(Short, self.symbol, str(candle[Short.col]))

        plot = self.create_plot(df, candles)

        return (
            Analysis(
                summary=f"{self.symbol} @ {candle['timestamp'].to_pydatetime().isoformat()}\n{message}",
                plot=plot,
            ),
            signal,
        )
