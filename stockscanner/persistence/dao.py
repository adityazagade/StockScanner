from abc import ABC, abstractmethod
from datetime import date, timedelta

from stockscanner.model.config import Config
from stockscanner.utils import FileUtils
import pandas as pd


class DAO(ABC):
    pass


class TickerDAO(DAO):
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


class TickerFileSystemDB(TickerDAO):
    def pe_schema_exists(self, symbol):
        return FileUtils.file_exists(f"{symbol}_pe.csv")

    def ohlc_schema_exists(self, symbol):
        return FileUtils.file_exists(f"{symbol}.csv")

    def save(self, symbol, entry):
        FileUtils.append_to_file(f"{symbol}.csv", entry)

    def read_all_data(self, symbol) -> pd.DataFrame:
        df = pd.read_csv(f"{symbol}.csv")
        df['Date'] = pd.to_datetime(df['Date'], format='%d-%b-%Y')
        return df

    def read_all_pe_data(self, symbol) -> pd.DataFrame:
        df = pd.read_csv(f"{symbol}_pe.csv")
        df['Date'] = pd.to_datetime(df['Date'], format='%d-%b-%Y')
        return df

    def read_data_for_date(self, symbol, d: date):
        df = pd.read_csv(f"{symbol}.csv")
        df['Date'] = pd.to_datetime(df['Date'], format='%d-%b-%Y')
        mask = (df['Date'] > (d - timedelta(5)).strftime("%d-%b-%Y")) & (df['Date'] <= d.strftime("%d-%b-%Y"))
        return (df.loc[mask]).iloc[-1]

    def save_pe_data(self, symbol, entry):
        FileUtils.append_to_file(f"{symbol}_pe.csv", entry)


class DAOManager:
    manager = None

    def __init__(self, db) -> None:
        self.dao = {}
        from stockscanner.persistence import dao_factory
        self.dao["ticker_dao"] = (dao_factory.get_ticker_dao(db))

    def get_dao_for_ticker(self) -> TickerDAO:
        return self.dao["ticker_dao"]

    @classmethod
    def get_instance(cls):
        config = Config.load_config()
        if DAOManager.manager is None:
            DAOManager.manager = DAOManager(config["db"])
        return DAOManager.manager
