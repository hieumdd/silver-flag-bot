from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional

import pandas as pd


@dataclass
class GetIntradayOptions:
    symbol: str
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    resolution: str = "1m"

    def __post_init__(self):
        start_date, *_, end_date = pd.bdate_range(
            end=datetime.today().date(),
            periods=7,
        )
        self.start_date = self.start_date if self.start_date is not None else start_date
        self.end_date = self.end_date if self.end_date is not None else end_date
