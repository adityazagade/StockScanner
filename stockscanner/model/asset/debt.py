from datetime import date
from typing import List

from stockscanner.model.asset.asset import Asset, Trade
from stockscanner.model.asset.asset_type import AssetType
from stockscanner.model.asset.holding import Holding, HoldingBuilder
from stockscanner.persistence.dao_manager import DAOManager
from stockscanner.utils import Constants


class Debt(Asset):
    def __init__(self) -> None:
        super().__init__()
        self.type = AssetType.DEBT
        self.__debt_instruments: List[Holding] = []
        self.__trade_book: List[Trade] = list()

    def get_invested_amount(self):
        invested_amount = 0
        for debt in self.__debt_instruments:
            invested_amount += debt.get_invested_amount()
        return invested_amount

    def get_current_value(self):
        curr_value = 0
        for debt in self.__debt_instruments:
            curr_value += debt.get_present_value()
        return curr_value

    def get_value_as_of_date(self, d: date):
        val = 0
        for debt in self.__debt_instruments:
            val += debt.get_value_as_of_date(d)
        return val

    def add(self, **kwargs):
        symbol: str = kwargs.get("symbol")
        quantity: float = kwargs.get("quantity")
        d: date = kwargs.get("date")
        price: float = kwargs.get("price")

        if price <= 0 or quantity <= 0:
            return

        for debt in self.__debt_instruments:
            if debt.symbol == symbol:
                debt.add_entry(d, quantity, price)
                self.__trade_book.append(Trade("buy", d, price, quantity))
                return

        debt = HoldingBuilder(symbol) \
            .with_entry(d, quantity, price) \
            .build()

        self.__debt_instruments.append(debt)
        self.__trade_book.append(Trade("buy", d, price, quantity))

    def remove(self, **kwargs):
        symbol = kwargs.get("symbol")
        for debt in self.__debt_instruments:
            if debt.symbol == symbol:
                debt.remove_entries(**kwargs)
                break

    def add_by_amount(self, amount: float, d: date = date.today()):
        for debt in self.__debt_instruments:
            if debt.symbol == Constants.SAVINGS_ACC:
                quantity = amount / len(self.__debt_instruments)
                price = 1
            else:
                dao = DAOManager.get_instance().get_dao_for_ticker()
                data = dao.read_data_for_date(debt.symbol, d)
                price = float(data['Close'])
                quantity = (amount / price) / len(self.__debt_instruments)
            self.add(symbol=debt.symbol, quantity=quantity, price=price, date=d)

    def reduce_by_amount(self, amount: float, d: date = date.today()):
        for debt in self.__debt_instruments:
            if debt.symbol == Constants.SAVINGS_ACC:
                quantity = amount / len(self.__debt_instruments)
            else:
                dao = DAOManager.get_instance().get_dao_for_ticker()
                data = dao.read_data_for_date(debt.symbol, d)
                quantity = (amount / float(data['Close'])) / len(self.__debt_instruments)
            self.remove(symbol=debt.symbol, quantity=quantity, date=d)

    def get_trade_book(self):
        return self.__trade_book
