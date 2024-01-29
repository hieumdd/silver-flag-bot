from dataclasses import dataclass

import emoji

from trading.signal.enum import SignalType


@dataclass
class Signal:
    type_: SignalType
    timestamp: str
    value: str
    message: str

    def __repr__(self):
        return emoji.emojize(
            " ".join(
                [
                    self.type_.emoji_short_code,
                    self.timestamp,
                    self.type_.message,
                    self.value,
                    self.message,
                ]
            )
        )
