from trading.strategy.atr_trailing_stop import ATRTrailingStop
from trading.strategy_params.strategy_params import StrategyParams


def test_strategy_params():
    strategy_params = StrategyParams(ATRTrailingStop("VN30F1M"))
    print(strategy_params.to_html())
