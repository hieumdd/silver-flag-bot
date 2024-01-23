from dataclasses import dataclass, field
from datetime import date


@dataclass
class GetIntradayOptions:
    symbol: str
    from_date: date = field(default_factory=date.today)
    to_date: date = field(default_factory=date.today)
    page_index: int = 1
    page_size: int = 1000
    resolution: str = "1m"
    ascending: bool = False
