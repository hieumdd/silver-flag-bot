from datetime import datetime
import pandas as pd
from typing import Protocol

from ssi.client import SSIClient
from ssi.options import GetIntradayOptions


class DataProvider(Protocol):
    def get(self) -> pd.DataFrame:
        pass


class IntradayDataProvider(DataProvider):
    client = SSIClient()

    def get(self, symbol: str) -> pd.DataFrame:
        df = pd.DataFrame(
            self.client.get_intraday(GetIntradayOptions(symbol))
        ).drop_duplicates()

        def create_timestamp(row):
            return datetime.combine(
                datetime.strptime(row["TradingDate"], "%d/%m/%Y").date(),
                datetime.strptime(row["Time"], "%H:%M:%S").time(),
            )

        ohlc_columns = ["value", "open", "high", "low", "close", "volume"]

        df = (
            df.set_index(pd.DatetimeIndex(df.apply(create_timestamp, axis=1)))
            .sort_index()
            .rename(str.lower, axis=1)
            .astype({col_name: float for col_name in ohlc_columns})
        )

        return df[["symbol", *ohlc_columns]]
