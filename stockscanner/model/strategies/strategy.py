import logging
from abc import ABC, abstractmethod

from stockscanner.model.reporting.report import Report

logger = logging.getLogger(__name__)


class Strategy(ABC):
    def __init__(self):
        self.name = None

    @abstractmethod
    def check_if_constraints_are_matched(self, hist_data, **kwargs) -> bool:
        pass

    @abstractmethod
    def backtest(self, df, **kwargs) -> Report:
        pass

    def apply_to_portfolio(self, **kwargs):
        pass
