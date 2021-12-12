from datetime import date
from typing import List
from stockscanner.model.asset import Asset
from stockscanner.model.strategy import Strategy


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

    def do_rebalance(self, curr_date: date, **kwargs):
        curr_eq_weight = self.get_eq_weight(curr_date)
        curr_debt_weight = self.get_debt_weight(curr_date)
        curr_gold_weight = self.get_gold_weight(curr_date)
        curr_cash_weight = self.get_cash_weight(curr_date)

        val_as_of_today = self.get_value_as_of_date(curr_date)
        # change in weight
        amount = (kwargs.get("eq_weight", 0) - curr_eq_weight) * val_as_of_today
        if amount > 0:
            self.get_eq_asset().add_by_amount(abs(amount), curr_date)
        elif amount < 0:
            self.get_eq_asset().reduce_by_amount(abs(amount), curr_date)

        amount = (kwargs.get("debt_weight", 0) - curr_debt_weight) * val_as_of_today
        if amount > 0:
            self.get_debt_asset().add_by_amount(abs(amount), curr_date)
        elif amount < 0:
            self.get_debt_asset().reduce_by_amount(abs(amount), curr_date)

        amount = (kwargs.get("gold_wight", 0) - curr_gold_weight) * val_as_of_today
        if amount > 0:
            self.get_gold_asset().add_by_amount(abs(amount), curr_date)
        elif amount < 0:
            self.get_gold_asset().reduce_by_amount(abs(amount), curr_date)

        amount = (kwargs.get("cash_weight", 0) - curr_cash_weight) * val_as_of_today
        if amount > 0:
            self.get_cash_asset().add_by_amount(abs(amount), curr_date)
        elif amount < 0:
            self.get_cash_asset().reduce_by_amount(abs(amount), curr_date)

    def get_eq_weight(self, curr_date=None) -> float:
        for a in self.__assets:
            if a.type == Asset.EQUITY:
                if curr_date:
                    return a.get_value_as_of_date(curr_date) / self.get_value_as_of_date(curr_date)
                else:
                    return a.get_current_value() / self.get_current_value()
        return 0

    def get_debt_weight(self, curr_date=None) -> float:
        for a in self.__assets:
            if a.type == Asset.DEBT:
                if curr_date:
                    return a.get_value_as_of_date(curr_date) / self.get_value_as_of_date(curr_date)
                else:
                    return a.get_current_value() / self.get_current_value()
        return 0

    def get_gold_weight(self, curr_date=None) -> float:
        for a in self.__assets:
            if a.type == Asset.GOLD:
                if curr_date:
                    return a.get_value_as_of_date(curr_date) / self.get_value_as_of_date(curr_date)
                else:
                    return a.get_current_value() / self.get_current_value()
        return 0

    def get_cash_weight(self, curr_date=None) -> float:
        for a in self.__assets:
            if a.type == Asset.CASH:
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

    def get_eq_asset(self) -> Asset:
        for a in self.__assets:
            if a.type == Asset.EQUITY:
                return a
        raise Exception("Asset does not exist")

    def get_cash_asset(self) -> Asset:
        for a in self.__assets:
            if a.type == Asset.CASH:
                return a
        raise Exception("Asset does not exist")

    def get_debt_asset(self) -> Asset:
        for a in self.__assets:
            if a.type == Asset.DEBT:
                return a
        raise Exception("Asset does not exist")

    def get_gold_asset(self) -> Asset:
        for a in self.__assets:
            if a.type == Asset.GOLD:
                return a
        raise Exception("Asset does not exist")

    def __str__(self) -> str:
        current_details = f"Total Invested: ${self.total_invested()}, Current Value: ${self.get_current_value()}"
        change_logs = '\r\n'.join(map(str, self.get_change_logs()))
        trade_book = '\r\n'.join(map(str, self.get_trade_book()))
        return f"{current_details} \r\n + {change_logs} \r\n {trade_book}"

    def get_trade_book(self) -> list:
        return self.get_eq_asset().get_trade_book()
