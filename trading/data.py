from datetime import datetime
import pandas as pd
from typing import Protocol

from ssi.client import SSIClient
from ssi.options import GetIntradayOptions
from trading.timeframe import Timeframe


class DataProvider(Protocol):
    client = SSIClient()

    def get(self, *args, **kwargs) -> pd.DataFrame:
        pass

    def create_timestamp(self, row):
        return datetime.combine(
            datetime.strptime(row["TradingDate"], "%d/%m/%Y").date(),
            datetime.strptime(row["Time"], "%H:%M:%S").time(),
        )


class IntradayDataProvider(DataProvider):
    def __init__(self, timeframe: Timeframe):
        self.timeframe = timeframe

    def get(self, symbol: str) -> pd.DataFrame:
        data = self.client.get_intraday(GetIntradayOptions(symbol))
        df = pd.DataFrame(data).drop_duplicates()
        df["timestamp"] = pd.DatetimeIndex(df.apply(self.create_timestamp, axis=1))

        ohlc_columns = {
            "open": "first",
            "high": "max",
            "low": "min",
            "close": "last",
            "volume": "sum",
        }

        df = (
            (
                df.set_index(df["timestamp"], drop=False)
                .sort_index()
                .rename(str.lower, axis=1)
                .astype({col_name: float for col_name in ohlc_columns})
            )[["symbol", "timestamp", *ohlc_columns.keys()]]
            .resample(self.timeframe.interval)
            .agg(ohlc_columns)
            .dropna()
        )

        return df
