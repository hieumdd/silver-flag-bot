from types import SimpleNamespace

import pandas_ta as ta
import mplfinance as mpf

from trading.timeframe import TF_5MIN
from trading.data_provider import IntradayDataProvider
from trading.signal import Long, Short
from trading.strategy.interface import Strategy


class ATRTrailingStop(Strategy):
    data_provider = IntradayDataProvider(TF_5MIN)
    params = SimpleNamespace(
        atr_length=10,
        n_loss_sensitivity=1,
        ma_period=2,
        linreg_length=2,
        linreg_offset=1,
    )

    def populate_indicators(self, df):
        df["ATR"] = ta.atr(
            df["high"],
            df["low"],
            df["close"],
            length=self.params.atr_length,
        )
        df["NLOSS"] = df["ATR"] * self.params.n_loss_sensitivity
        df["PRICE"] = df["open"]

        df["SRC"] = ta.linreg(
            df["PRICE"],
            self.params.linreg_length,
            self.params.linreg_offset - 1,
        )

        df = df.dropna()

        df["ATR_TRAILING_STOP"] = 0.0
        for i in range(1, len(df)):
            src = df.loc[df.index[i], "SRC"]
            prev_src = df.loc[df.index[i - 1], "SRC"]
            prev_atr_trailing_stop = df.loc[df.index[i - 1], "ATR_TRAILING_STOP"]
            n_loss = df.loc[df.index[i], "NLOSS"]

            atr_trailing_stop = 0

            if src > prev_atr_trailing_stop and prev_src > prev_atr_trailing_stop:
                atr_trailing_stop = max(prev_atr_trailing_stop, src - n_loss)
            elif src < prev_atr_trailing_stop and prev_src < prev_atr_trailing_stop:
                atr_trailing_stop = min(prev_atr_trailing_stop, src + n_loss)
            elif src > prev_atr_trailing_stop:
                atr_trailing_stop = src - n_loss
            else:
                atr_trailing_stop = src + n_loss

            df.loc[df.index[i], "ATR_TRAILING_STOP"] = atr_trailing_stop

        df["MA"] = ta.ema(df["SRC"], self.params.ma_period)

        return df

    def populate_signals(self, df):
        df.loc[
            (df["SRC"] > df["ATR_TRAILING_STOP"])
            & (ta.cross(df["MA"], df["ATR_TRAILING_STOP"], above=True) == 1),
            Long.value_col,
        ] = df["PRICE"]

        df.loc[
            (df["SRC"] < df["ATR_TRAILING_STOP"])
            & (ta.cross(df["MA"], df["ATR_TRAILING_STOP"], above=False) == 1),
            Short.value_col,
        ] = df["PRICE"]

        return df

    def populate_subplots(self, df):
        return [
            mpf.make_addplot(
                df["ATR_TRAILING_STOP"],
                panel=0,
                width=0.75,
                secondary_y=False,
                label="ATR Trailing Stop",
            ),
            mpf.make_addplot(
                df["MA"],
                panel=0,
                width=0.75,
                linestyle="--",
                secondary_y=False,
                label="MA",
            ),
        ]
