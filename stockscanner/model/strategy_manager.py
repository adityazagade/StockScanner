from typing import List

from stockscanner.model.exceptions import StrategyNotFoundException
from stockscanner.model.report import Report
from stockscanner.model.strategy import Strategy, MarketMovementBasedAllocation
from stockscanner.persistence import dao_factory


class StrategyManager:
    def __init__(self, config) -> None:
        self.strategies: List[Strategy] = [MarketMovementBasedAllocation()]
        self.ticker_dao = dao_factory.get_ticker_dao(config["db"])

    def back_test_strategy(self, sname, **kwargs):
        try:
            s: Strategy = self.get_by_name(sname)
            return s.backtest(self.ticker_dao, **kwargs)
        except StrategyNotFoundException:
            print(f"Strategy {sname} not found")
        except Exception as e:
            print(f"backtesting the strategy {sname} failed: {e}")

    def get_by_name(self, sname) -> Strategy:
        for s in self.strategies:
            if s.name == sname:
                return s
        raise StrategyNotFoundException(sname)
