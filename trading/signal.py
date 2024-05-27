from abc import ABC
from dataclasses import dataclass

import emoji


@dataclass
class Signal(ABC):
    def __init_subclass__(cls, tag: str, emoji_code: str) -> None:
        cls.tag = tag
        cls.emoji_code = emoji_code
        cls.value_col = f"{cls.tag}Value"
        cls.marker_col = f"{cls.tag}Marker"

    def to_html(self):
        return emoji.emojize(f"{self.emoji_code} {self.tag.upper()} {self.symbol}")


@dataclass
class Long(Signal, tag="Long", emoji_code=":green_circle:"):
    pass


@dataclass
class Short(Signal, tag="Short", emoji_code=":red_circle:"):
    pass
