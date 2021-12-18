import logging
from datetime import date
from typing import List

from stockscanner.model.exceptions.exceptions import PortfolioCreationException
from stockscanner.model.portfolio.portfolio import Portfolio
from stockscanner.persistence.dao_manager import DAOManager
from stockscanner.utils import Constants

logger = logging.getLogger(__name__)


class PortfolioBuilder:
    def __init__(self) -> None:
        super().__init__()
        self.portfolio_name = "Default Portfolio"
        self.initial_cap: int = 0
        self.eq_weight: float = 0
        self.debt_weight: float = 0
        self.gold_weight: float = 0
        self.cash_weight: float = 0
        self.creation_date: date = date.today()
        self.stocks = []
        self.debts = []
        self.ticker_dao = DAOManager.get_instance().get_dao_for_ticker()

    def with_initial_capital(self, amount: int):
        self.initial_cap = amount
        return self

    def with_eq_weight(self, weight: float):
        self.eq_weight = weight
        return self

    def with_debt_weight(self, weight: float):
        self.debt_weight = weight
        return self

    def with_gold_weight(self, weight: float):
        self.gold_weight = weight
        return self

    def with_cash_weight(self, weight: float):
        self.cash_weight = weight
        return self

    def with_stocks(self, stocks: List[str]):
        self.stocks = stocks
        return self

    def with_debts(self, debts: List[str]):
        self.debts = debts
        return self

    def with_name(self, name):
        self.portfolio_name = name
        return self

    def on_date(self, creation_date: date):
        self.creation_date = creation_date
        return self

    def build(self, strict: bool = False) -> Portfolio:
        try:
            self.validate(strict)

            p: Portfolio = Portfolio(self.portfolio_name)

            eq_value = self.eq_weight * self.initial_cap
            for stock in self.stocks:
                stock_price_action_as_on_date = self.ticker_dao.read_data_for_date(ticker=stock, d=self.creation_date)
                eq_price = stock_price_action_as_on_date['Close']
                eq_quantity = (eq_value / eq_price) / len(self.stocks)
                p.add_stock(symbol=stock, date=self.creation_date, quantity=eq_quantity, price=eq_price)

            debt_value = self.debt_weight * self.initial_cap
            for debt in self.debts:
                if debt == Constants.SAVINGS_ACC:
                    debt_price = 1
                    debt_quantity = (debt_value / debt_price) / len(self.debts)
                    p.add_debt(symbol=debt, date=self.creation_date, quantity=debt_quantity, price=debt_price)
                else:
                    debt_price_action = self.ticker_dao.read_data_for_date(ticker=debt, d=self.creation_date)
                    debt_price = debt_price_action['Close']
                    debt_quantity = (debt_value / debt_price) / len(self.debts)
                    p.add_debt(symbol=debt, date=self.creation_date, quantity=debt_quantity, price=debt_price)

            # TODO: gold

            cash_value = self.cash_weight * self.initial_cap
            p.add_cash(cash_value)

            return p
        except Exception as e:
            logger.error(f"Could not create portfolio: {e}")
            raise PortfolioCreationException()

    def validate(self, strict):
        total_weight = self.eq_weight + self.debt_weight + self.gold_weight + self.cash_weight
        if strict:
            if total_weight != 1:
                raise Exception("Error creating portfolio. Sum of weights not equal to 1")
        else:
            if total_weight > 1:
                self.cash_weight -= abs(total_weight - 1)
            elif total_weight < 1:
                self.cash_weight += abs(1 - total_weight)

        # validate stocks
        for stock in self.stocks:
            if not self.ticker_dao.is_valid_ticker(stock):
                raise Exception("Invalid ticker added or Ticker data not available")
