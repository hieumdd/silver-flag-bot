from datetime import datetime
from functools import reduce
import operator

import pandas as pd
import pandas_ta as ta

from ssi.client_model import GetIntradayOptions
from trading.signal.enum import SignalEnum
from trading.strategy.interface import Strategy


class MultiMA(Strategy):
    _range = range(5, 105, 5)

    def get_options(self):
        start_date, *_, end_date = pd.bdate_range(
            end=datetime.today().date(),
            periods=7,
        )
        return GetIntradayOptions(
            symbol="VN30F1M",
            start_date=start_date.to_pydatetime(),
            end_date=end_date.to_pydatetime(),
        )

    def populate_indicators(self, df):
        _df = df.copy()

        _df["RSI_CROSS_ABOVE"] = ta.cross_value(ta.rsi(_df["close"]), 50)
        _df["RSI_CROSS_BELOW"] = ta.cross_value(ta.rsi(_df["close"]), 50, above=False)
        for length in self._range:
            _df[f"EMA_{length}"] = ta.ema(_df["close"], length=length)
        return _df

    def populate_signals(self, df):
        _df = df.copy()

        for length in self._range:
            _df[f"EMA_{length}_DIFF"] = _df[f"EMA_{length}"] - _df[
                f"EMA_{length}"
            ].shift(1)

        _df.loc[
            reduce(
                operator.and_,
                [_df[f"EMA_{length}_DIFF"] > 0 for length in self._range]
                + [_df["RSI_CROSS_ABOVE"] == 1],
            ),
            SignalEnum.LONG_ENTRY,
        ] = True

        _df.loc[
            reduce(
                operator.and_,
                [_df[f"EMA_{length}_DIFF"] < 0 for length in self._range]
                + [_df["RSI_CROSS_BELOW"] == 1],
            ),
            SignalEnum.SHORT_ENTRY,
        ] = True

        return _df
