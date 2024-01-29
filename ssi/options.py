from dataclasses import dataclass
from datetime import date


@dataclass
class GetIntradayOptions:
    symbol: str
    start_date: date
    end_date: date
    resolution: str = "1m"
    ascending: bool = True
