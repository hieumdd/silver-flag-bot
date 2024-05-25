from dataclasses import dataclass
from functools import partial

import emoji


@dataclass
class Signal:
    tag: str
    emoji_code: str
    symbol: str
    value: str

    @property
    def value_col(self):
        return f"{self.tag}Value"

    @property
    def marker_col(self):
        return f"{self.tag}Marker"

    def to_html(self):
        return emoji.emojize(f"{self.emoji_code} {self.tag.upper()} {self.symbol}")


Long = partial(tag="Long", emoji_code=":green_circle:")
Short = partial(tag="Short", emoji_code=":red_circle:")
