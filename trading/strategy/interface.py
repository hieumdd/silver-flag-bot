from abc import ABC, abstractmethod
from dataclasses import dataclass
from functools import partial
import io
from typing import ClassVar, Optional
from types import SimpleNamespace

import numpy as np
import pandas as pd
import mplfinance as mpf

from logger import get_logger
from trading.data_provider import DataProvider
from trading.signal import Signal, Long, Short
from trading.analysis import Analysis


logger = get_logger(__name__)


@dataclass
class Strategy(ABC):
    symbol: str
    data_provider: ClassVar[DataProvider]
    params: ClassVar[SimpleNamespace]

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
        df.loc[:, [Long.value_col, Short.value_col]] = (pd.NA, pd.NA)
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
            markersize=300,
        )

        df[Long.marker_col] = np.nan
        df.loc[df[Long.value_col].notnull(), Long.marker_col] = df["high"]
        long_signal_plot = (
            []
            if df[Long.value_col].isna().all()
            else [
                signal_plot(
                    df[Long.marker_col] + 0.5,
                    marker=r"$\uparrow$",
                    color="mediumseagreen",
                )
            ]
        )

        df.loc[df[Short.value_col].notnull(), Short.marker_col] = df["low"]
        short_signal_plot = (
            []
            if df[Short.value_col].isna().all()
            else [
                signal_plot(
                    df[Short.marker_col] - 0.5,
                    marker=r"$\downarrow$",
                    color="lightcoral",
                )
            ]
        )

        plot = io.BytesIO()
        mpf.plot(
            df,
            type="candle",
            tight_layout=True,
            volume=True,
            figratio=(16, 9),
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

        long_entry = not pd.isna(candle[Long.value_col])
        short_entry = not pd.isna(candle[Short.value_col])

        signal = None
        if long_entry and not short_entry:
            signal = Long(self.symbol, str(candle[Long.value_col]))
        elif short_entry and not long_entry:
            signal = Short(self.symbol, str(candle[Short.value_col]))

        plot = self.create_plot(df, candles)
        summary = f"{self.symbol} @ {candle['timestamp'].to_pydatetime().isoformat()}\n{message}"

        return (Analysis(summary=summary, plot=plot), signal)


@dataclass
class StrategyParams:
    strategy: Strategy

    def to_html(self):
        params_dict = self.strategy.params.__dict__.items()
        params_html = "\n".join(
            [f"=== {self.strategy.__class__.__name__} ==="]
            + [f"{key}: {value}" for key, value in params_dict]
        )
        return f'<pre><code class="language-yaml">{params_html}</code></pre>'
