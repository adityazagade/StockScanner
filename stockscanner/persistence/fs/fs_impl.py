from datetime import date, timedelta

import pandas as pd

from stockscanner.persistence.dao import TickerDAO
from stockscanner.utils import FileUtils


class TickerFileSystemDB(TickerDAO):
    data: dict = {}

    def __init__(self) -> None:
        super().__init__()

    def pe_schema_exists(self, symbol):
        return FileUtils.file_exists(f"{symbol}_pe.csv")

    def ohlc_schema_exists(self, symbol):
        return FileUtils.file_exists(f"{symbol}.csv")

    def read_all_data(self, symbol) -> pd.DataFrame:
        if symbol not in TickerFileSystemDB.data:
            df = pd.read_csv(f"{symbol}.csv")
            df['Date'] = pd.to_datetime(df['Date'], format='%d-%b-%Y')
            TickerFileSystemDB.data[symbol] = df
        return TickerFileSystemDB.data[symbol].copy()

    def read_all_pe_data(self, symbol) -> pd.DataFrame:
        if f"{symbol}_pe" not in TickerFileSystemDB.data:
            df = pd.read_csv(f"{symbol}_pe.csv")
            df['Date'] = pd.to_datetime(df['Date'], format='%d-%b-%Y')
            df.rename(columns={'P/E': 'P_E', 'P/B': 'P_B', 'Div Yield':'Div_Yield'}, inplace=True)
            TickerFileSystemDB.data[f"{symbol}_pe"] = df
        return TickerFileSystemDB.data[f"{symbol}_pe"].copy()

    def read_data_for_date(self, symbol, d: date):
        if symbol in TickerFileSystemDB.data:
            df = TickerFileSystemDB.data[symbol].copy()
        else:
            df = self.read_all_data(symbol)
        mask = (df['Date'] > (d - timedelta(5)).strftime("%d-%b-%Y")) & (df['Date'] <= d.strftime("%d-%b-%Y"))
        return (df.loc[mask]).iloc[-1]

    def save_headers(self, ticker, headers):
        self.save(ticker, headers)

    def save_pe_headers(self, ticker, headers):
        self.save_pe_data(ticker, headers)

    def save(self, symbol, entry):
        # TODO: I should check if the data already exist. If yes, the don't add. Otherwise need to update the satic
        #  variable data and also the csv file.
        FileUtils.append_to_file(f"{symbol}.csv", "\n" + entry)

    def save_pe_data(self, symbol, entry):
        # TODO: I should check if the data already exist. If yes, the don't add. Otherwise need to update the satic
        #  variable data and also the csv file.
        FileUtils.append_to_file(f"{symbol}_pe.csv", "\n" + entry)
