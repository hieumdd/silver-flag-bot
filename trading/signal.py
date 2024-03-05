from dataclasses import dataclass
import io

import emoji


@dataclass
class SignalType:
    flag_col: str
    marker_col: str
    message: str
    emoji_short_code: str


LongEntry = SignalType("LongEntry", "LongMarker", "LONG", ":green_circle:")
ShortEntry = SignalType("ShortEntry", "ShortMarker", "SHORT", ":red_circle:")


@dataclass
class Signal:
    type_: SignalType
    value: str

    def to_html(self, symbol: str):
        return emoji.emojize(
            f"{self.type_.emoji_short_code} {symbol} @ <code>{self.value}</code> {self.type_.message}"
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
