from dataclasses import dataclass
import io

import emoji


@dataclass
class Analysis:
    summary: str
    plot: io.BytesIO

    def to_html(self):
        return emoji.emojize(f":blue_circle: {self.summary}")
