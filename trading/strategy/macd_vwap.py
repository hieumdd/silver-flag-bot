import pandas_ta as ta

from data.provider import IntradayDataProvider
from trading.signal.enum import LongEntry, ShortEntry
from trading.strategy.interface import Strategy


class MACDVWAP(Strategy):
    data_provider = IntradayDataProvider()

    def populate_indicators(self, df):
        _df = df.copy()

        _df[["MACD", "MACD_H", "MACD_S"]] = ta.macd(_df["close"])
        _df["VWAP"] = ta.vwap(_df["high"], _df["low"], _df["close"], _df["volume"])
        _df[["ADX", "DI+", "DI-"]] = ta.adx(_df["high"], _df["low"], _df["close"])

        return _df

    def populate_signals(self, df):
        _df = df.copy()

        for signal_type in [LongEntry, ShortEntry]:
            _df[[signal_type.flag_col, signal_type.tag_col]] = (None, None)

        _df.loc[
            (ta.cross(_df["MACD"], _df["MACD_S"]) == 1)
            & (_df["close"] > _df["VWAP"])
            & (_df["ADX"] > 25),
            [LongEntry.flag_col, LongEntry.tag_col],
        ] = (True, "MACD Cross Up & Close > VWAP")

        _df.loc[
            (ta.cross(_df["MACD"], _df["MACD_S"], above=False) == 1)
            & (_df["close"] < _df["VWAP"])
            & (_df["ADX"] > 25),
            [ShortEntry.flag_col, ShortEntry.tag_col],
        ] = (True, "MACD Cross Down & Close < VWAP")

        return _df
