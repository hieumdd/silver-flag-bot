from dataclasses import dataclass


@dataclass
class SignalType:
    flag_col: str
    tag_col: str
    message: str
    emoji_short_code: str


LongEntry = SignalType("LongEntry", "LongEntryTag", "LONG", ":green_circle:")
ShortEntry = SignalType("ShortEntry", "ShortEntryTag", "SHORT", ":red_circle:")
