from abc import ABC, abstractmethod

from stockscanner.utils import FileUtils
import pandas as pd


class DAO(ABC):
    pass


class TickerDAO(DAO):
    @abstractmethod
    def schema_exists(self, symbol):
        pass

    @abstractmethod
    def save(self, symbol, entry):
        pass

    @abstractmethod
    def read_all_data(self, symbol) -> pd.DataFrame:
        pass


class TickerFileSystemDB(TickerDAO):
    # overriding abstract method
    def schema_exists(self, symbol):
        return FileUtils.file_exists(f"{symbol}.csv")

    def save(self, symbol, entry):
        FileUtils.append_to_file(f"{symbol}.csv", entry)

    def read_all_data(self, symbol) -> pd.DataFrame:
        df = pd.read_csv(f"{symbol}.csv")
        df['Date'] = pd.to_datetime(df['Date'], format='%d-%b-%Y')
        return df


class DAOManager:
    manager = None

    def __init__(self) -> None:
        self.dao = [TickerDAO(), ]

    def get_dao_for_ticker(self, symbol) -> TickerDAO:
        pass

    @classmethod
    def get_instance(cls):
        if DAOManager.manager is None:
            return DAOManager()
        return DAOManager.manager
