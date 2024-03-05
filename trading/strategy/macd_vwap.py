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
        _df = df.copy()

        _df[["MACD", "MACD_H", "MACD_S"]] = ta.macd(_df["close"])
        _df["VWAP"] = ta.vwap(_df["high"], _df["low"], _df["close"], _df["volume"])
        _df[["ADX", "DI+", "DI-"]] = ta.adx(_df["high"], _df["low"], _df["close"])

        return _df

    def populate_signals(self, df):
        _df = df.copy()

        _df.loc[
            (ta.cross(_df["MACD"], _df["MACD_S"]) == 1)
            & (_df["close"] > _df["VWAP"])
            & (_df["ADX"] > self.adx_threshold),
            LongEntry.flag_col,
        ] = True

        _df.loc[
            (ta.cross(_df["MACD"], _df["MACD_S"], above=False) == 1)
            & (_df["close"] < _df["VWAP"])
            & (_df["ADX"] > self.adx_threshold),
            ShortEntry.flag_col,
        ] = True

        return _df

    def populate_subplots(self, df):
        _df = df.copy()

        long_marker = _df[LongEntry.flag_col] == True
        short_marker = _df[ShortEntry.flag_col] == True
        _df.loc[long_marker, "LongMarker"] = _df.loc[long_marker]["high"]
        _df.loc[short_marker, "ShortMarker"] = _df.loc[short_marker]["low"]

        return [
            mpf.make_addplot(
                _df["VWAP"],
                panel=0,
                width=1,
                secondary_y=False,
            ),
            mpf.make_addplot(
                _df["MACD"],
                panel=2,
                width=1,
                secondary_y=False,
            ),
            mpf.make_addplot(
                _df["MACD_S"],
                panel=2,
                width=1,
                linestyle="--",
                secondary_y=False,
            ),
            mpf.make_addplot(
                _df["ADX"],
                panel=3,
                width=1,
                secondary_y=False,
            ),
            mpf.make_addplot(
                _df["ADX"].apply(lambda _: self.adx_threshold),
                panel=3,
                width=1,
                linestyle="--",
                secondary_y=False,
            ),
            *(
                []
                if _df["LongMarker"].isnull().all()
                else [
                    mpf.make_addplot(
                        _df["LongMarker"],
                        type="scatter",
                        panel=0,
                        marker="^",
                        markersize=200,
                        color="lime",
                    )
                ]
            ),
            *(
                []
                if _df["ShortMarker"].isnull().all()
                else [
                    mpf.make_addplot(
                        _df["ShortMarker"],
                        type="scatter",
                        panel=0,
                        marker="v",
                        markersize=200,
                        color="pink",
                    )
                ]
            ),
        ]
