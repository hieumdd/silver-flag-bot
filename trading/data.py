from abc import abstractmethod
from datetime import datetime
import pandas as pd

from ssi.client import SSIClient
from trading.timeframe import Timeframe


class DataProvider:
    timeframe: Timeframe
    ohlc_columns = {
        "open": "first",
        "high": "max",
        "low": "min",
        "close": "last",
        "volume": "sum",
    }
    client = SSIClient()

    def __init__(self, timeframe: Timeframe):
        self.timeframe = timeframe

    @abstractmethod
    def get(self, *args, **kwargs) -> pd.DataFrame:
        pass

    def create_timestamp(self, row):
        return datetime.combine(
            datetime.strptime(row["TradingDate"], "%d/%m/%Y").date(),
            datetime.strptime(row["Time"], "%H:%M:%S").time(),
        )


class IntradayDataProvider(DataProvider):
    def get(self, symbol: str) -> pd.DataFrame:
        start_date, *_, end_date = pd.bdate_range(
            end=datetime.today().date(),
            periods=7,
        )
        data = self.client.get_intraday(symbol, start_date, end_date)

        df = pd.DataFrame(data).drop_duplicates()
        df["timestamp"] = pd.DatetimeIndex(df.apply(self.create_timestamp, axis=1))

        df = (
            (
                df.set_index(df["timestamp"], drop=False)
                .sort_index()
                .rename(str.lower, axis=1)
                .astype({col_name: float for col_name in self.ohlc_columns})
            )[["symbol", "timestamp", *self.ohlc_columns.keys()]]
            .resample(self.timeframe.interval)
            .agg(self.ohlc_columns)
            .dropna()
        )

        return df
