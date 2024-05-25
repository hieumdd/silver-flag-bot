from abc import abstractmethod
from dataclasses import dataclass
from datetime import datetime
import pandas as pd

from ssi.client import SSIClient
from trading.timeframe import Timeframe


@dataclass
class DataProvider:
    timeframe: Timeframe
    client = SSIClient()

    @abstractmethod
    def date_ranges(self) -> pd.DatetimeIndex:
        pass

    def get(self, symbol: str) -> pd.DataFrame:
        ohlc_columns = {
            "open": "first",
            "high": "max",
            "low": "min",
            "close": "last",
            "volume": "sum",
        }

        start_date, *_, end_date = self.date_ranges()
        data = self.client.get_intraday(symbol, start_date, end_date)

        df = pd.DataFrame(data).drop_duplicates()
        df["timestamp"] = pd.DatetimeIndex(
            df.apply(
                lambda row: datetime.combine(
                    datetime.strptime(row["TradingDate"], "%d/%m/%Y").date(),
                    datetime.strptime(row["Time"], "%H:%M:%S").time(),
                ),
                axis=1,
            )
        )

        df = (
            (
                df.set_index(df["timestamp"], drop=False)
                .sort_index()
                .rename(str.lower, axis=1)
                .astype({col_name: float for col_name in ohlc_columns})
            )[["symbol", "timestamp", *ohlc_columns.keys()]]
            .resample(self.timeframe.interval)
            .agg(ohlc_columns | {"timestamp": "last"})
            .dropna()
        )

        return df


class IntradayDataProvider(DataProvider):
    def date_ranges(self) -> pd.DatetimeIndex:
        return pd.bdate_range(end=datetime.today().date(), periods=7)
