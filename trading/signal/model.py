import emoji

class Signal:
    def __init__(self, message: str):
        self.message = message


class LongSignal(Signal):
    def to_message(self):
        return emoji.emojize(f":green_circle: {self.message}")


class ShortSignal(Signal):
    def to_message(self):
        return emoji.emojize(f":red_circle: {self.message}")
