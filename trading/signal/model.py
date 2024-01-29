from dataclasses import dataclass

import emoji

from trading.signal.enum import SignalType


@dataclass
class Signal:
    type_: SignalType
    symbol: str
    timestamp: str
    value: str
    message: str

    def __str__(self):
        return emoji.emojize(
            "\n".join(
                [
                    f"{self.type_.emoji_short_code} {self.symbol} @ <b><code>{self.value}</code></b> {self.type_.message}",
                    f"<tg-spoiler><b>Message</b>: {self.message}</tg-spoiler>",
                    f"<tg-spoiler><b>Timestamp</b>: {self.timestamp}</tg-spoiler>",
                ]
            )
        )
