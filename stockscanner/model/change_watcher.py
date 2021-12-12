from threading import Thread
import sys
import pandas as pd
import math

from pandas.core.reshape.merge import merge


class ChangeWatcher(Thread):
    def __init__(self):
        super().__init__()

    def run(self):
        # 1. load the date from the file system using the Ticker_DAO
        from stockscanner.persistence.dao import DAOManager
        dao = DAOManager.get_instance().get_dao_for_ticker()
        price_action = dao.read_all_data("NIFTY 50")  # pd.read_csv(sys.path[0] + "\\NIFTY 50.csv", delimiter=",")
        indicator_action = dao.read_all_pe_data("NIFTY 50")  # pd.read_csv(sys.path[0] + "\\NIFTY 50_pe.csv", delimiter=",")
        merge_pd = price_action.merge(indicator_action, how="left", on="Date")
        # print(merge_pd.dtypes)
        # print(merge_pd["P/E"].describe())
        merge_pd.sort_values("P/E", ascending=True, inplace=True)
        merge_pd["P/E_Range"] = pd.cut(merge_pd["P/E"],
                                       bins=(int(merge_pd["P/E"].max()) - int(merge_pd["P/E"].min() + 1)), precision=2,
                                       ordered=True)

        new_pd = merge_pd["P/E_Range"].value_counts() / merge_pd["P/E"].count()
        new_pd = new_pd.to_frame(name="Probablity")
        new_pd.sort_index(inplace=True)
        new_pd["P/E_Range"] = new_pd.index
        new_pd["Cumulative_Probablity"] = new_pd["Probablity"].cumsum()
        new_pd["Equity_Weightage"] = round(75 - (75 - 25) * new_pd["Cumulative_Probablity"], 2)
        new_pd["P/E_Range"] = new_pd["P/E_Range"].astype("string")
        # print(new_pd)

        last_dt = str(merge_pd["Date"].iloc[-1])
        last_cl = str(merge_pd["Close"].iloc[-1])
        last_pe = str(merge_pd["P/E"].iloc[-1])
        # print(last_dt + " " + last_cl + " " + last_pe)
        # X = u + z@
        cur_pe = 30  # X
        for index, row in new_pd.iterrows():
            cat_min = float(row["P/E_Range"].split(",")[0].split("(")[1])
            cat_max = float(row["P/E_Range"].split(",")[1].split("]")[0])
            if cat_min < cur_pe <= cat_max:
                print(row["Equity_Weightage"])

    def asset_allocation(self):
        pass

    def rebalance(self):
        pass
