from functools import reduce
import operator

import pandas_ta as ta

from trading.timeframe import TF_1MIN
from trading.data import IntradayDataProvider
from trading.signal import Long, Short
from trading.strategy.interface import Strategy


class MultiMA(Strategy):
    data_provider = IntradayDataProvider(TF_1MIN)

    def __init__(self, symbol: str, ma_ranges=range(5, 105, 5)):
        super().__init__(symbol)
        self.ma_ranges = ma_ranges

    def populate_indicators(self, df):
        df["RSI"] = ta.rsi(df["close"])
        df["RSI_CROSS_ABOVE"] = ta.cross_value(df["RSI"], 50)
        df["RSI_CROSS_BELOW"] = ta.cross_value(df["RSI"], 50, above=False)
        for length in self.ma_ranges:
            df[f"EMA_{length}"] = ta.ema(df["close"], length=length)

        return df

    def populate_signals(self, df):
        df.loc[
            reduce(
                operator.and_,
                [
                    df[f"EMA_{length}"] > df[f"EMA_{length}"].shift(1)
                    for length in self.ma_ranges
                ]
                + [df["RSI_CROSS_ABOVE"] == 1],
            ),
            Long.col,
        ] = df["close"]

        df.loc[
            reduce(
                operator.and_,
                [
                    df[f"EMA_{length}"] < df[f"EMA_{length}"].shift(1)
                    for length in self.ma_ranges
                ]
                + [df["RSI_CROSS_BELOW"] == 1],
            ),
            Short.col,
        ] = df["close"]

        return df
