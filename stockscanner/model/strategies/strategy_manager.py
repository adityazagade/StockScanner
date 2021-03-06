import logging
from typing import List

from stockscanner.model.config import Config
from stockscanner.model.exceptions.exceptions import StrategyNotFoundException
from stockscanner.model.reporting.report import Report
from stockscanner.model.strategies.buy_n_hold_strategy import BuyAndHold
from stockscanner.model.strategies.pe_based_allocations import PEBasedAllocation
from stockscanner.model.strategies.sip import SIP
from stockscanner.model.strategies.strategy import Strategy
from stockscanner.model.strategies.market_movement_based_allocation import MarketMovementBasedAllocation
from stockscanner.persistence import dao_factory
from stockscanner.persistence.dao import TickerDAO
from datetime import datetime

logger = logging.getLogger(__name__)


class StrategyManager:
    manager = None

    def __init__(self, config) -> None:
        self.strategies: List[Strategy] = [
            MarketMovementBasedAllocation(config["strategies"]["MarketMovementBasedAllocation"]["change_threshold"]),
            BuyAndHold(),
            SIP(),
            PEBasedAllocation(config["strategies"]["MarketMovementBasedAllocation"]["change_threshold"])
        ]
        self.ticker_dao: TickerDAO = dao_factory.get_ticker_dao(config["db"])

    def back_test_strategy(self, strategy_config) -> Report:
        strategy_name = strategy_config["strategy_name"]
        try:
            s: Strategy = self.get_by_name(strategy_name)
            s.init(strategy_config)
            date_time_obj = datetime.strptime(strategy_config["backtest_start_date"], '%d-%m-%Y').date()
            return s.backtest(self.ticker_dao, back_test_start_date=date_time_obj)
        except StrategyNotFoundException:
            logger.error(f"Strategy {strategy_name} not found")
        except Exception as e:
            logger.error(f"backtesting the strategy {strategy_name} failed: {e}")

    def get_by_name(self, sname) -> Strategy:
        for s in self.strategies:
            if s.name == sname:
                return s
        raise StrategyNotFoundException(sname)

    def get_all_strategies(self) -> List[Strategy]:
        return self.strategies

    @classmethod
    def get_instance(cls):
        config = Config.load_config()
        if StrategyManager.manager is None:
            StrategyManager.manager = StrategyManager(config)
        return StrategyManager.manager
