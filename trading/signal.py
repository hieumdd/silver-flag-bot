from abc import ABC
from dataclasses import dataclass
from typing import ClassVar

import emoji


@dataclass
class Signal(ABC):
    tag: ClassVar[str]
    emoji_code: ClassVar[str]

    @classmethod
    def value_col(cls):
        return f"{cls.tag}Value"

    @classmethod
    def marker_col(cls):
        return f"{cls.tag}Marker"

    def to_html(self):
        return emoji.emojize(f"{self.emoji_code} {self.tag.upper()} {self.symbol}")


@dataclass
class Long(Signal):
    tag = "Long"
    emoji_code = ":green_circle:"


@dataclass
class Short(Signal):
    tag = "Short"
    emoji_code = ":red_circle:"
