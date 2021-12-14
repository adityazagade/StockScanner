from datetime import date, timedelta
import pandas as pd
import sqlite3

from stockscanner.persistence.dao import TickerDAO
from datetime import datetime


class SqliteTickerDaoImpl(TickerDAO):
    def __init__(self, **kwargs) -> None:
        super().__init__()
        self.con = sqlite3.connect("data.db", check_same_thread=kwargs.get("check_same_thread", True))

    def save(self, symbol, entry):
        list = entry.split(",")
        d = (datetime.strptime(list[0].replace("\"", "").strip(), "%d-%b-%Y")).date()
        open = list[1].replace("\"", "").strip()
        high = list[2].replace("\"", "").strip()
        low = list[3].replace("\"", "").strip()
        close = list[4].replace("\"", "").strip()
        shares_traded = None
        try:
            shares_traded = float(list[5].replace("\"", "").strip())
        except Exception as e:
            pass
        turnover = None
        try:
            turnover = float(list[6].replace("\"", "").strip())
        except Exception as e:
            pass

        self.create_ohlc_table_if_not_exist(symbol)
        cur = self.con.cursor()
        table_name = symbol.strip().replace(" ", "_") + "_OHLC"
        cur.execute(f"INSERT INTO {table_name} VALUES (?,?,?,?,?,?,?)",
                    [d, open, high, low, close, shares_traded, turnover])
        self.con.commit()
        cur.close()

    def save_pe_data(self, ticker, entry):
        list = entry.split(",")
        d = (datetime.strptime(list[0].replace("\"", "").strip(), "%d-%b-%Y")).date()
        p_e = list[1].replace("\"", "").strip()
        p_b = list[2].replace("\"", "").strip()
        div_yield = list[3].replace("\"", "").strip()
        self.create_pe_table_if_not_exist(ticker)
        cur = self.con.cursor()
        table_name = ticker.strip().replace(" ", "_") + "_PE"
        cur.execute(f"INSERT INTO {table_name} VALUES (?,?,?,?)", [d, p_e, p_b, div_yield])
        self.con.commit()
        cur.close()

    def read_all_data(self, symbol) -> pd.DataFrame:
        table_name = symbol.strip().replace(" ", "_") + "_OHLC"
        if not self.table_exist(table_name):
            raise Exception("Table does not exist")
        df = pd.read_sql_query(f"SELECT * from {table_name} ORDER BY date(Date)", self.con)
        df['Date'] = pd.to_datetime(df['Date'], format='%Y-%m-%d')
        return df

    def read_all_pe_data(self, symbol) -> pd.DataFrame:
        table_name = symbol.strip().replace(" ", "_") + "_PE"
        if not self.table_exist(table_name):
            raise Exception("Table does not exist")
        df = pd.read_sql_query(f"SELECT * from {table_name} ORDER BY date(DATE)", self.con)
        df['Date'] = pd.to_datetime(df['Date'], format='%Y-%m-%d')
        return df

    def pe_schema_exists(self, ticker):
        table_name = ticker.strip().replace(" ", "_") + "_PE"
        return self.table_exist(f"{table_name}")

    def ohlc_schema_exists(self, ticker):
        table_name = ticker.strip().replace(" ", "_") + "_OHLC"
        return self.table_exist(f"{table_name}")

    def read_data_for_date(self, ticker: str, d: date):
        end_date = d
        start_date = (d - timedelta(5))
        table_name = ticker.strip().replace(" ", "_") + "_OHLC"
        df = pd.read_sql_query(
            f"select * from {table_name} where date(DATE) between "
            f"date('{start_date}') and date('{end_date}') order by date(DATE)",
            self.con)
        return df.iloc[-1]

    def __del__(self):
        self.con.close()

    def table_exist(self, table_name):
        table_name = table_name.strip().replace(" ", "_")
        cursor = self.con.cursor()
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
        exist = len(cursor.fetchall()) > 0
        cursor.close()
        return exist

    def create_ohlc_table_if_not_exist(self, symbol):
        table_name = symbol.strip().replace(" ", "_") + "_OHLC"
        if not self.table_exist(table_name):
            cursor = self.con.cursor()
            cursor.execute(
                f"CREATE TABLE {table_name} "
                f"(Date date primary key, Open real, High real, Low real, Close real, Shares_Traded real, Turnover real)")
            self.con.commit()
            cursor.close()

    def create_pe_table_if_not_exist(self, symbol):
        table_name = symbol.strip().replace(" ", "_") + "_PE"
        if not self.table_exist(table_name):
            cursor = self.con.cursor()
            cursor.execute(
                f"CREATE TABLE {table_name} (Date date primary key, P_E real, P_B real, Div_Yield real)")
            self.con.commit()
            cursor.close()
