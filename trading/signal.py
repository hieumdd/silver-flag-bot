from dataclasses import dataclass
import html

import emoji


@dataclass
class SignalType:
    tag: str
    emoji_short_code: str

    @property
    def col(self):
        return f"{self.tag}Value"


Long = SignalType("Long", ":green_circle:")
Short = SignalType("Short", ":green_circle:")


@dataclass
class Signal:
    type_: SignalType
    symbol: str
    value: str

    def to_html(self):
        return emoji.emojize(
            f"{self.type_.emoji_short_code} {self.type_.tag.upper()} {self.symbol} @ <code>{html.escape(self.value)}</code>"
        )
