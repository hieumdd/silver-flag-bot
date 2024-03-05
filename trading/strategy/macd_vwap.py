import pandas_ta as ta
import mplfinance as mpf

from trading.timeframe import TF_1MIN
from trading.data import IntradayDataProvider
from trading.signal.model import LongEntry, ShortEntry
from trading.strategy.interface import Strategy


class MACDVWAP(Strategy):
    data_provider = IntradayDataProvider(TF_1MIN)

    adx_threshold = 25

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
            LongEntry.flag_col,
        ] = True

        df.loc[
            (ta.cross(df["MACD"], df["MACD_S"], above=False) == 1)
            & (df["close"] < df["VWAP"])
            & (df["ADX"] > self.adx_threshold),
            ShortEntry.flag_col,
        ] = True

        return df

    def populate_subplots(self, df):
        return [
            mpf.make_addplot(
                df["VWAP"],
                panel=0,
                width=1,
                secondary_y=False,
            ),
            mpf.make_addplot(
                df["MACD"],
                panel=2,
                width=1,
                secondary_y=False,
            ),
            mpf.make_addplot(
                df["MACD_S"],
                panel=2,
                width=1,
                linestyle="--",
                secondary_y=False,
            ),
            mpf.make_addplot(
                df["ADX"],
                panel=3,
                width=1,
                secondary_y=False,
            ),
            mpf.make_addplot(
                df["ADX"].apply(lambda _: self.adx_threshold),
                panel=3,
                width=1,
                linestyle="--",
                secondary_y=False,
            ),
        ]
