from dataclasses import dataclass
from datetime import datetime

import emoji


@dataclass
class Line:
    name: str
    buy: str
    sell: str

    def to_html(self):
        return emoji.emojize(
            f"{self.name} :green_circle: <code>{self.buy}</code> :red_circle: <code>{self.sell}</code>"
        )


@dataclass
class Report:
    updated_at: datetime
    lines: list[Line]

    def to_html(self):
        return "\n".join(
            [
                self.updated_at.isoformat(timespec="seconds"),
                *[line.to_html() for line in self.lines],
            ]
        )
