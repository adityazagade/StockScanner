from abc import ABC, abstractmethod
from datetime import date


class Asset(ABC):
    def __init__(self) -> None:
        super().__init__()
        self.type = ""

    @abstractmethod
    def add(self, **kwargs):
        pass

    @abstractmethod
    def remove(self, **kwargs):
        pass

    @abstractmethod
    def get_current_value(self):
        pass

    @abstractmethod
    def get_invested_amount(self):
        pass

    @abstractmethod
    def get_value_as_of_date(self, d: date):
        pass

    @abstractmethod
    def add_by_amount(self, amount: float, d: date = date.today()):
        pass

    @abstractmethod
    def reduce_by_amount(self, amount: float, d: date = date.today()):
        pass

    @abstractmethod
    def get_trade_book(self):
        pass


class Trade:
    def __init__(self, action, d, price, quantity) -> None:
        self.action = action
        self.date = d
        self.price = price
        self.quantity = quantity

    def __str__(self) -> str:
        return f"{self.action} {self.date} {self.price} {self.quantity}"