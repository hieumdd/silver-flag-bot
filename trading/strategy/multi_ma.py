from functools import reduce
import operator

import pandas_ta as ta

from data.provider import IntradayDataProvider
from trading.signal.model import LongEntry, ShortEntry
from trading.strategy.interface import Strategy


class MultiMA(Strategy):
    data_provider = IntradayDataProvider()
    _range = range(5, 105, 5)

    def populate_indicators(self, df):
        _df = df.copy()

        _df["RSI"] = ta.rsi(_df["close"])
        _df["RSI_CROSS_ABOVE"] = ta.cross_value(_df["RSI"], 50)
        _df["RSI_CROSS_BELOW"] = ta.cross_value(_df["RSI"], 50, above=False)
        for length in self._range:
            _df[f"EMA_{length}"] = ta.ema(_df["close"], length=length)
        return _df

    def populate_signals(self, df):
        _df = df.copy()

        _df.loc[
            reduce(
                operator.and_,
                [
                    _df[f"EMA_{length}"] > _df[f"EMA_{length}"].shift(1)
                    for length in self._range
                ]
                + [_df["RSI_CROSS_ABOVE"] == 1],
            ),
            LongEntry.flag_col,
        ] = True

        _df.loc[
            reduce(
                operator.and_,
                [
                    _df[f"EMA_{length}"] < _df[f"EMA_{length}"].shift(1)
                    for length in self._range
                ]
                + [_df["RSI_CROSS_BELOW"] == 1],
            ),
            ShortEntry.flag_col,
        ] = True

        return _df
