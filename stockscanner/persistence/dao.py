from abc import ABC, abstractmethod
from datetime import date

import pandas as pd


class DAO(ABC):
    pass


class TickerDAO(DAO):
    @abstractmethod
    def is_valid_ticker(self, symbol):
        pass

    @abstractmethod
    def save(self, symbol, entry):
        pass

    @abstractmethod
    def save_pe_data(self, ticker, entry):
        pass

    @abstractmethod
    def read_all_data(self, symbol) -> pd.DataFrame:
        pass

    @abstractmethod
    def read_all_pe_data(self, symbol) -> pd.DataFrame:
        pass

    @abstractmethod
    def pe_schema_exists(self, ticker):
        pass

    @abstractmethod
    def ohlc_schema_exists(self, ticker):
        pass

    @abstractmethod
    def read_data_for_date(self, ticker, d: date):
        pass

    def save_headers(self, ticker, headers):
        pass

    def save_pe_headers(self, ticker, headers):
        pass


class PortfolioDAO(DAO):
    pass


class StrategyDAO(DAO):
    pass
