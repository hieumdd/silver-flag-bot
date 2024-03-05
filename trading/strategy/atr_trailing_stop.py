import numpy as np
import pandas_ta as ta

from trading.timeframe import TF_5MIN
from trading.data import IntradayDataProvider
from trading.signal import LongEntry, ShortEntry
from trading.strategy.interface import Strategy


class ATRTrailingStop(Strategy):
    data_provider = IntradayDataProvider(TF_5MIN)

    atr_length = 10
    n_loss_sensitivity = 2

    def populate_indicators(self, df):
        df["ATR"] = ta.atr(
            df["high"],
            df["low"],
            df["close"],
            length=self.atr_length,
        )
        df["NLOSS"] = df["ATR"] * self.n_loss_sensitivity

        df = df.dropna()

        df["ATR_TRAILING_STOP"] = np.nan
        df.loc[df.index[0], "ATR_TRAILING_STOP"] = 0.0

        for i in range(1, len(df)):
            close = df.loc[df.index[i], "close"]
            prev_close = df.loc[df.index[i - 1], "close"]
            prev_atr_trailing_stop = df.loc[df.index[i - 1], "ATR_TRAILING_STOP"]
            n_loss = df.loc[df.index[i], "NLOSS"]

            atr_trailing_stop = 0

            if close > prev_atr_trailing_stop and prev_close > prev_atr_trailing_stop:
                atr_trailing_stop = max(prev_atr_trailing_stop, close - n_loss)
            elif close < prev_atr_trailing_stop and prev_close < prev_atr_trailing_stop:
                atr_trailing_stop = min(prev_atr_trailing_stop, close + n_loss)
            elif close > prev_atr_trailing_stop:
                atr_trailing_stop = close - n_loss
            else:
                atr_trailing_stop = close + n_loss

            df.loc[df.index[i], "ATR_TRAILING_STOP"] = atr_trailing_stop

        df["EMA"] = ta.ema(df["close"], 1, talib=False)

        return df

    def populate_signals(self, df):
        df.loc[
            (df["close"] > df["ATR_TRAILING_STOP"])
            & (ta.cross(df["EMA"], df["ATR_TRAILING_STOP"], above=True) == 1),
            LongEntry.flag_col,
        ] = True

        df.loc[
            (df["close"] < df["ATR_TRAILING_STOP"])
            & (ta.cross(df["EMA"], df["ATR_TRAILING_STOP"], above=False) == 1),
            ShortEntry.flag_col,
        ] = True

        return df
