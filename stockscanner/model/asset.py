from abc import ABC, abstractmethod
from typing import List
from datetime import date, timedelta

from stockscanner.persistence.dao import DAOManager


class Entry:
    def __init__(self, d: date, quantity: int, price: float) -> None:
        self.date = d
        self.quantity = quantity
        self.price = price


class Asset(ABC):
    def __init__(self) -> None:
        super().__init__()

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


class Holding:
    def __init__(self, symbol, history: List[Entry]) -> None:
        if len(history) <= 0:
            raise Exception("Cannot add a holding without history")
        self.symbol = symbol
        self.history: List[Entry] = history

    def get_average_buy_price(self) -> float:
        mcap = 0
        for entry in self.history:
            mcap += entry.quantity * entry.price
        quantity = self.get_quantity()
        if quantity == 0:
            raise Exception("Total quantity == 0")
        return mcap / self.get_quantity()

    def get_quantity(self) -> int:
        quantity = 0
        for entry in self.history:
            quantity += entry.quantity
        return quantity

    def get_present_value(self) -> float:
        return self.get_quantity() * self.get_current_price()

    def get_current_price(self) -> float:
        dao = DAOManager.get_instance().get_dao_for_ticker(self.symbol)
        df = dao.read_all_data(self.symbol)
        mask = (df['Date'] >= date.today().strftime("%d-%b-%Y")) & (df['Date'] < (
                date.today() - timedelta(5)).strftime("%d-%b-%Y"))
        return float(df.loc[mask][-1]['Close'])


class Equity(Asset):
    def __init__(self) -> None:
        super().__init__()
        self.type = "equity"
        self.__stocks: List[Holding] = []

    def add(self, **kwargs):
        symbol: str = kwargs.get("symbol")
        quantity: int = kwargs.get("quantity")
        d: date = kwargs.get("date")
        price: float = kwargs.get("price")
        for stock in self.__stocks:
            if stock.symbol == symbol:
                stock.history.append(Entry(d, quantity, price))
                return
        self.__stocks.append(Holding(symbol, [Entry(d, quantity, price)]))

    def remove(self, **kwargs):
        symbol = kwargs.get("symbol")
        quantity = kwargs.get("quantity")
        for stock in self.__stocks:
            if stock.symbol == symbol:
                if stock.get_quantity() < quantity:
                    raise Exception("Cannot remove more than what is present")
                if quantity > stock.history[0].quantity:
                    q_tmp = stock.history[0].quantity
                    stock.history.pop(0)
                    self.remove(symbol=symbol, quantity=quantity - q_tmp)
                elif quantity == stock.history[0].quantity:
                    stock.history.pop(0)
                else:
                    stock.history[0].quantity = (quantity - stock.history[0].quantity)
                break

    def get_current_value(self):
        curr_value = 0
        for stock in self.__stocks:
            curr_value += stock.get_present_value()
        return curr_value

    def get_invested_amount(self):
        invested_amount = 0
        for stock in self.__stocks:
            for entry in stock.history:
                invested_amount += entry.price * entry.quantity
        return invested_amount


class Debt(Asset):
    def __init__(self) -> None:
        super().__init__()
        self.__debt_instruments: List[Holding] = []

    def get_invested_amount(self):
        invested_amount = 0
        for debt in self.__debt_instruments:
            for entry in debt.history:
                invested_amount += entry.price * entry.quantity
        return invested_amount

    def get_current_value(self):
        curr_value = 0
        for debt in self.__debt_instruments:
            curr_value += debt.get_present_value()
        return curr_value

    def add(self, **kwargs):
        symbol: str = kwargs.get("symbol")
        quantity: int = kwargs.get("quantity")
        d: date = kwargs.get("date")
        price: float = kwargs.get("price")
        for debt in self.__debt_instruments:
            if debt.symbol == symbol:
                debt.history.append(Entry(d, quantity, price))
                break

    def remove(self, **kwargs):
        symbol = kwargs.get("symbol")
        quantity = kwargs.get("quantity")
        for debt in self.__debt_instruments:
            if debt.symbol == symbol:
                if debt.get_quantity() < quantity:
                    raise Exception("Cannot remove more than what is present")
                if quantity > debt.history[0].quantity:
                    q_tmp = debt.history[0].quantity
                    debt.history.pop(0)
                    self.remove(symbol=symbol, quantity=quantity - q_tmp)
                elif quantity == debt.history[0].quantity:
                    debt.history.pop(0)
                else:
                    debt.history[0].quantity = (quantity - debt.history[0].quantity)
                break


# class Gold(Asset):
#     def __init__(self) -> None:
#         super().__init__()
#         self.type = "gold"


class Cash(Asset):
    def __init__(self, amount: float) -> None:
        super().__init__()
        self.type = "cash"
        self.amount = amount

    def remove(self, **kwargs):
        if self.amount < kwargs.get("amount"):
            raise Exception("Cannot remove more amount than what you have")
        self.amount -= kwargs.get("amount")

    def get_current_value(self) -> float:
        return self.amount

    def add(self, **kwargs):
        self.amount += kwargs.get("amount")

    def get_invested_amount(self) -> float:
        return self.amount
