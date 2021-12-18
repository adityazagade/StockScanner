from datetime import date
from typing import List

from stockscanner.model.asset.asset import Asset, Trade
from stockscanner.model.asset.asset_type import AssetType
from stockscanner.model.asset.holding import Holding, HoldingBuilder
from stockscanner.persistence.dao_manager import DAOManager


class Equity(Asset):
    def __init__(self) -> None:
        super().__init__()
        self.type = AssetType.EQUITY
        self.__stocks: List[Holding] = []
        self.__trade_book: List[Trade] = list()

    def add(self, **kwargs):
        symbol: str = kwargs.get("symbol")
        quantity: float = kwargs.get("quantity")
        d: date = kwargs.get("date")
        price: float = kwargs.get("price")
        for stock in self.__stocks:
            if stock.symbol == symbol:
                stock.add_entry(d, quantity, price)
                self.__trade_book.append(Trade("buy", d, price, quantity))
                return
        hld = HoldingBuilder(symbol) \
            .with_entry(d, quantity, price) \
            .build()
        self.__stocks.append(hld)
        self.__trade_book.append(Trade("buy", d, price, quantity))

    def remove(self, **kwargs):
        symbol = kwargs.get("symbol")
        for stock in self.__stocks:
            if stock.symbol == symbol:
                stock.remove_entries(**kwargs)
                break

    def add_by_amount(self, amount: float, d: date = date.today()):
        dao = DAOManager.get_instance().get_dao_for_ticker()
        data = dao.read_data_for_date("NIFTY 50", d)
        quantity = amount / float(data['Close'])
        self.add(symbol="NIFTY 50", quantity=quantity, price=float(data['Close']), date=d)

    def reduce_by_amount(self, amount: float, d: date = date.today()):
        dao = DAOManager.get_instance().get_dao_for_ticker()
        data = dao.read_data_for_date("NIFTY 50", d)
        quantity = amount / float(data['Close'])
        self.remove(symbol="NIFTY 50", quantity=quantity, date=d, price=data['Close'])

    def get_current_value(self):
        curr_value = 0
        for stock in self.__stocks:
            curr_value += stock.get_present_value()
        return curr_value

    def get_value_as_of_date(self, d: date):
        val = 0
        for stock in self.__stocks:
            val += stock.get_value_as_of_date(d)
        return val

    def get_invested_amount(self):
        invested_amount = 0
        for stock in self.__stocks:
            invested_amount += stock.get_invested_amount()
        return invested_amount

    def get_trade_book(self):
        return self.__trade_book
