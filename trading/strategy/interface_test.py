import pytest

from trading.strategy.atr_trailing_stop import ATRTrailingStop
from trading.strategy.macd_vwap import MACDVWAP
from trading.strategy.multi_ma import MultiMA


strategies = [
    ATRTrailingStop,
    MACDVWAP,
    MultiMA,
]


@pytest.mark.parametrize(
    "strategy",
    [strategy("VN30F1M") for strategy in strategies],
    ids=[strategy.__name__ for strategy in strategies],
)
class TestStrategy:
    def test_generate_indicators(self, strategy):
        df = strategy.generate_indicators()
        assert df is not None

    def test_generate_signals(self, strategy):
        df = strategy.generate_signals()
        assert df is not None

    def test_analyze(self, strategy):
        analysis, _ = strategy.analyze()
        assert analysis
