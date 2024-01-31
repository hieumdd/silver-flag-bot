from dataclasses import dataclass, field

import emoji


@dataclass
class SignalType:
    flag_col: str
    message: str
    emoji_short_code: str


LongEntry = SignalType("LongEntry", "LONG", ":green_circle:")
ShortEntry = SignalType("ShortEntry", "SHORT", ":red_circle:")


@dataclass
class Signal:
    type_: SignalType
    symbol: str
    timestamp: str
    value: str

    def to_html(self):
        return emoji.emojize(
            "\n".join(
                [
                    f"{self.type_.emoji_short_code} {self.symbol} @ <b><code>{self.value}</code></b> {self.type_.message}",
                    f"<tg-spoiler><b>Timestamp</b>: {self.timestamp}</tg-spoiler>",
                ]
            )
        )
