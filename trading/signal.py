from dataclasses import dataclass
import io

import emoji


@dataclass
class SignalType:
    tag: str
    emoji_short_code: str

    @property
    def value_col(self):
        return f"{self.tag}Value"


Long = SignalType("Long", ":green_circle:")
Short = SignalType("Short", ":green_circle:")


@dataclass
class Signal:
    type_: SignalType
    value: str

    def to_html(self, symbol: str):
        return emoji.emojize(
            f"{self.type_.emoji_short_code} {symbol} @ <code>{self.value}</code> {self.type_.tag.upper()}"
        )


@dataclass
class Analysis:
    strategy: str
    symbol: str
    timestamp: str
    plot: io.BytesIO

    def to_html(self):
        return emoji.emojize(
            f":blue_circle: {self.strategy} :: {self.symbol} @ {self.timestamp}"
        )
