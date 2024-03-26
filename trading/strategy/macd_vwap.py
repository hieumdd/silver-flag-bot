import pandas_ta as ta
import mplfinance as mpf

from trading.timeframe import TF_1MIN
from trading.data import IntradayDataProvider
from trading.signal import Long, Short
from trading.strategy.interface import Strategy


class MACDVWAP(Strategy):
    data_provider = IntradayDataProvider(TF_1MIN)

    def __init__(self, symbol: str, adx_threshold=25):
        super().__init__(symbol)
        self.adx_threshold = adx_threshold

    def populate_indicators(self, df):
        df[["MACD", "MACD_H", "MACD_S"]] = ta.macd(df["close"])
        df["VWAP"] = ta.vwap(df["high"], df["low"], df["close"], df["volume"])
        df[["ADX", "DI+", "DI-"]] = ta.adx(df["high"], df["low"], df["close"])

        return df

    def populate_signals(self, df):
        df.loc[
            (ta.cross(df["MACD"], df["MACD_S"]) == 1)
            & (df["close"] > df["VWAP"])
            & (df["ADX"] > self.adx_threshold),
            Long.value_col,
        ] = df["close"]

        df.loc[
            (ta.cross(df["MACD"], df["MACD_S"], above=False) == 1)
            & (df["close"] < df["VWAP"])
            & (df["ADX"] > self.adx_threshold),
            Short.value_col,
        ] = df["close"]

        return df

    def populate_subplots(self, df):
        return [
            mpf.make_addplot(
                df["VWAP"],
                panel=0,
                width=1,
                secondary_y=False,
                label="VWAP",
            ),
            mpf.make_addplot(
                df["MACD"],
                panel=2,
                width=1,
                secondary_y=False,
                label="MACD",
            ),
            mpf.make_addplot(
                df["MACD_S"],
                panel=2,
                width=1,
                linestyle="--",
                secondary_y=False,
                label="MACD_S",
            ),
            mpf.make_addplot(
                df["ADX"],
                panel=3,
                width=1,
                secondary_y=False,
                label="ADX",
            ),
            mpf.make_addplot(
                df["ADX"].apply(lambda _: self.adx_threshold),
                panel=3,
                width=1,
                linestyle="--",
                secondary_y=False,
            ),
        ]
