import numpy as np
import pandas_ta as ta
import mplfinance as mpf

from data.provider import IntradayDataProvider
from trading.signal.model import LongEntry, ShortEntry
from trading.strategy.interface import Strategy


class ATRTrailingStop(Strategy):
    data_provider = IntradayDataProvider()

    atr_length = 10
    n_loss_sensitivity = 2

    def populate_indicators(self, df):
        _df = df.copy()

        _df["ATR"] = ta.atr(
            _df["high"],
            _df["low"],
            _df["close"],
            length=self.atr_length,
        )
        _df["NLOSS"] = _df["ATR"] * self.n_loss_sensitivity

        _df = _df.dropna()

        _df["ATR_TRAILING_STOP"] = np.nan
        _df.loc[_df.index[0], "ATR_TRAILING_STOP"] = 0.0

        def set_atr_trailing_stop(
            close: float,
            prev_close: float,
            prev_atr_trailing_stop: float,
            nloss: float,
        ):
            if close > prev_atr_trailing_stop and prev_close > prev_atr_trailing_stop:
                return max(prev_atr_trailing_stop, close - nloss)
            elif close < prev_atr_trailing_stop and prev_close < prev_atr_trailing_stop:
                return min(prev_atr_trailing_stop, close + nloss)
            elif close > prev_atr_trailing_stop:
                return close - nloss
            else:
                return close + nloss

        for i in range(1, len(_df)):
            _df.loc[_df.index[i], "ATR_TRAILING_STOP"] = set_atr_trailing_stop(
                _df.loc[_df.index[i], "close"],
                _df.loc[_df.index[i - 1], "close"],
                _df.loc[_df.index[i - 1], "ATR_TRAILING_STOP"],
                _df.loc[_df.index[i], "NLOSS"],
            )

        _df["EMA"] = ta.ema(_df["close"], 1, talib=False)

        return _df

    def populate_signals(self, df):
        _df = df.copy()

        _df.loc[
            (_df["close"] > _df["ATR_TRAILING_STOP"])
            & (ta.cross(_df["EMA"], _df["ATR_TRAILING_STOP"], above=True) == 1),
            LongEntry.flag_col,
        ] = True

        _df.loc[
            (_df["close"] < _df["ATR_TRAILING_STOP"])
            & (ta.cross(_df["EMA"], _df["ATR_TRAILING_STOP"], above=False) == 1),
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
