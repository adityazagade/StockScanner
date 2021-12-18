from datetime import date, timedelta
from typing import List

from stockscanner.model.config import Config
from stockscanner.persistence.dao_manager import DAOManager


class Entry:
    def __init__(self, d: date, quantity: float, price: float) -> None:
        self.date = d
        self.quantity = quantity
        self.price = price


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

    def get_quantity(self) -> float:
        quantity = 0
        for entry in self.history:
            quantity += entry.quantity
        return quantity

    def get_present_value(self) -> float:
        return self.get_quantity() * self.get_current_price()

    def get_current_price(self) -> float:
        dao = DAOManager.get_instance().get_dao_for_ticker()
        df = dao.read_all_data(self.symbol)
        mask = (df['Date'] > (date.today() - timedelta(5)).strftime("%d-%b-%Y")) & (
                df['Date'] <= date.today().strftime("%d-%b-%Y"))
        return float((df.loc[mask]).iloc[-1]['Close'])

    def get_price_as_of_date(self, d) -> float:
        dao = DAOManager.get_instance().get_dao_for_ticker()
        df = dao.read_all_data(self.symbol)
        mask = (df['Date'] >= (d - timedelta(5)).strftime("%d-%b-%Y")) & (df['Date'] <= d.strftime("%d-%b-%Y"))
        return float((df.loc[mask]).iloc[-1]['Close'])

    def get_value_as_of_date(self, d) -> float:
        return self.get_quantity() * self.get_price_as_of_date(d)

    def get_invested_amount(self):
        for entry in self.history:
            return entry.price * entry.quantity

    def add_entry(self, d, quantity, price):
        self.history.append(Entry(d, quantity, price))

    def remove_entries(self, **kwargs):
        quantity = kwargs.get("quantity")
        d = kwargs.get("date")
        price = kwargs.get("price")
        if self.get_quantity() < quantity:
            raise Exception("Cannot remove more than what is present")
        if quantity > self.history[0].quantity:
            q_tmp = self.history[0].quantity
            self.history.pop(0)
            # self.__trade_book.append(Trade("sell", d, price, q_tmp))
            self.remove_entries(quantity=quantity - q_tmp, date=d, price=price)
        elif quantity == self.history[0].quantity:
            self.history.pop(0)
            # self.__trade_book.append(Trade("sell", d, price, quantity))
        else:
            self.history[0].quantity = (self.history[0].quantity - quantity)
            # self.__trade_book.append(Trade("sell", d, price, quantity))


class SavingsAccount(Holding):

    def __init__(self, symbol, history: List[Entry]) -> None:
        super().__init__(symbol, history)
        self.interest_rate = Config.load_config()["interest_rate"]

    def get_average_buy_price(self) -> float:
        sum = 0
        for entry in self.history:
            sum += entry.price * entry.quantity
        return sum

    def get_present_value(self) -> float:
        sum = 0
        d = date.today()
        for entry in self.history:
            if entry.date < d:
                principle = entry.quantity * entry.price
                daily_rate = self.interest_rate / 365 * 100
                value = principle * pow((1 + daily_rate), (d - entry.date).days)
                sum += value
        return sum

    def get_current_price(self) -> float:
        return 1

    def get_price_as_of_date(self, d) -> float:
        return 1

    def get_value_as_of_date(self, d) -> float:
        sum = 0
        for entry in self.history:
            if entry.date < d:
                principle = entry.quantity * entry.price
                daily_rate = self.interest_rate / 365 * 100
                value = principle * pow((1 + daily_rate), (d - entry.date).days)
                sum += value
        return sum

    def get_quantity(self) -> float:
        return super().get_quantity()

    def get_invested_amount(self):
        return super().get_invested_amount()

    def remove_entries(self, **kwargs):
        quantity = kwargs.get("quantity")
        d = kwargs.get("date")
        value_to_be_removed = quantity * self.get_current_price()

        curr_value = self.get_value_as_of_date(d)
        expected_value = curr_value - value_to_be_removed

        while curr_value > expected_value:

            for entry in self.history:
                entry.quantity -= 10

