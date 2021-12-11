from typing import List
from stockscanner.model import asset
from stockscanner.model.asset import Asset
from stockscanner.model.strategy import Strategy


class Portfolio:
    def __init__(self, name) -> None:
        self.name = name
        self.description = ""
        self.__assets: List[asset] = list()
        self.change_logs = list()
        self.strategy = None

    def add_asset(self, a: Asset):
        self.__assets.append(a)

    def set_description(self, description):
        self.description = description

    def get_returns(self):
        pass

    def get_xirr(self):
        pass

    def total_invested(self):
        total_invested = 0
        for a in self.__assets:
            total_invested += a.get_invested_amount()
        return total_invested

    def current_value(self):
        curr_val = 0
        for a in self.__assets:
            curr_val += a.get_current_value()
        return curr_val

    def apply_strategy(self, s: Strategy):
        self.strategy = s

    def do_rebalance(self, s):
        pass
