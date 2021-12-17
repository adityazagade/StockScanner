from datetime import date
from typing import List

from stockscanner.model.asset.asset_type import AssetType
from stockscanner.model.exceptions.exceptions import AssetNotFoundException
from stockscanner.model.asset.asset import Asset, Equity, Cash, Debt
from stockscanner.model.strategies.strategy import Strategy


class Portfolio:
    def __init__(self, name) -> None:
        self.name = name
        self.description = ""
        self.__assets: List[Asset] = list()
        self.__change_logs = list()
        self.__strategy = None

    def get_change_logs(self):
        return self.__change_logs

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

    def apply_strategy(self, s: Strategy):
        self.__strategy = s

    def rebalance_by_weights(self, **kwargs):
        curr_date: date = kwargs.get("curr_date")

        curr_eq_weight = self.get_asset_weight(AssetType.EQUITY, curr_date)
        curr_debt_weight = self.get_asset_weight(AssetType.DEBT, curr_date)
        curr_gold_weight = self.get_asset_weight(AssetType.GOLD, curr_date)
        curr_cash_weight = self.get_asset_weight(AssetType.CASH, curr_date)

        val_as_of_today = self.get_value_as_of_date(curr_date)
        # change in weight
        amount = (kwargs.get("eq_weight", 0) - curr_eq_weight) * val_as_of_today
        if amount > 0:
            self.get_asset(AssetType.EQUITY).add_by_amount(abs(amount), curr_date)
        elif amount < 0:
            self.get_asset(AssetType.EQUITY).reduce_by_amount(abs(amount), curr_date)

        amount = (kwargs.get("debt_weight", 0) - curr_debt_weight) * val_as_of_today
        if amount > 0:
            self.get_asset(AssetType.DEBT).add_by_amount(abs(amount), curr_date)
        elif amount < 0:
            self.get_asset(AssetType.DEBT).reduce_by_amount(abs(amount), curr_date)

        amount = (kwargs.get("gold_weight", 0) - curr_gold_weight) * val_as_of_today
        if amount > 0:
            self.get_asset(AssetType.GOLD).add_by_amount(abs(amount), curr_date)
        elif amount < 0:
            self.get_asset(AssetType.GOLD).reduce_by_amount(abs(amount), curr_date)

        amount = (kwargs.get("cash_weight", 0) - curr_cash_weight) * val_as_of_today
        if amount > 0:
            self.get_asset(AssetType.CASH).add_by_amount(abs(amount), curr_date)
        elif amount < 0:
            self.get_asset(AssetType.CASH).reduce_by_amount(abs(amount), curr_date)

        message = f"Total Invested: ${self.total_invested()}, " \
                  f"Current Value: ${self.get_value_as_of_date(curr_date)} \r\n " \
                  f"eq: {self.get_asset_weight(AssetType.EQUITY, curr_date)} " \
                  f"debt: {self.get_asset_weight(AssetType.DEBT, curr_date)} " \
                  f"gold: {self.get_asset_weight(AssetType.GOLD, curr_date)} " \
                  f"cash: {self.get_asset_weight(AssetType.CASH, curr_date)}"
        self.add_rebalance_logs(f"Portfolio rebalanced on {curr_date} \n + ${message}")

    def get_asset_weight(self, asset: AssetType, curr_date=None):
        for a in self.__assets:
            if a.type == asset:
                if curr_date:
                    return a.get_value_as_of_date(curr_date) / self.get_value_as_of_date(curr_date)
                else:
                    return a.get_current_value() / self.get_current_value()
        return 0

    def get_current_value(self):
        sum = 0
        for a in self.__assets:
            sum += a.get_current_value()
        return sum

    def add_rebalance_logs(self, message):
        self.__change_logs.append(message)

    def get_value_as_of_date(self, d: date):
        val = 0
        for a in self.__assets:
            val += a.get_value_as_of_date(d)
        return val

    def get_asset(self, asset_type: AssetType):
        for a in self.__assets:
            if a.type == asset_type:
                return a
        raise AssetNotFoundException()

    def __str__(self) -> str:
        current_details = f"Total Invested: ${self.total_invested()}, Current Value: ${self.get_current_value()}"
        change_logs = '\r\n'.join(map(str, self.get_change_logs()))
        trade_book = '\r\n'.join(map(str, self.get_trade_book()))
        return f"{current_details} \r\n + {change_logs} \r\n {trade_book}"

    def get_trade_book(self) -> list:
        return self.get_asset(AssetType.EQUITY).get_trade_book()

    def get_strategy(self) -> Strategy:
        return self.__strategy

    def add_stock(self, **kwargs):
        try:
            eq = self.get_asset(AssetType.EQUITY)
        except AssetNotFoundException:
            eq = Equity()
            self.__assets.append(eq)
        eq.add(**kwargs)

    def add_debt(self, **kwargs):
        try:
            dt = self.get_asset(AssetType.DEBT)
        except AssetNotFoundException:
            dt = Debt()
            self.__assets.append(dt)
        dt.add(**kwargs)

    def add_cash(self, cash_value):
        try:
            cash_asset = self.get_asset(AssetType.CASH)
            cash_asset.add_by_amount(cash_value)
        except AssetNotFoundException:
            cash_asset = Cash(cash_value)
            self.__assets.append(cash_asset)
