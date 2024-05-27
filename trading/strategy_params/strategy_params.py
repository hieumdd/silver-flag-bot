from dataclasses import dataclass
import yaml
from yattag import Doc

import emoji

from trading.strategy.interface import Strategy


@dataclass
class StrategyParams:
    strategy: Strategy

    def to_html(self):
        doc, tag, text = Doc().tagtext()
        strategy_name = self.strategy.__class__.__name__
        doc.asis(emoji.emojize(f":blue_circle: {strategy_name}"))
        with tag("pre"):
            with tag("code", klass="language-yaml"):
                text(yaml.dump(self.strategy.params.__dict__))

        return doc.getvalue()
