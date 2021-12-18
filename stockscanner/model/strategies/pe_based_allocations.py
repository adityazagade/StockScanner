import logging
from datetime import timedelta

import pandas as pd

from stockscanner.model.asset.asset_type import AssetType
from stockscanner.model.exceptions.exceptions import PortfolioCreationException
from stockscanner.model.portfolio.portfolio import Portfolio
from stockscanner.model.portfolio.portfolio_builder import PortfolioBuilder
from stockscanner.model.reporting.report import Report
from stockscanner.model.strategies.strategy import Strategy
from stockscanner.persistence.dao import TickerDAO
from stockscanner.utils.DateUtils import get_df_between_dates

logger = logging.getLogger(__name__)


class PEBasedAllocation(Strategy):
    def __init__(self, percent_change) -> None:
        super().__init__()
        self.name = "PEBasedAllocation"
        self.change_threshold = percent_change / 100
        self.pivot = 0

    def check_if_constraints_are_matched(self, hist_data: pd.DataFrame, **kwargs) -> bool:
        if self.pivot == 0:
            raise Exception(f"pivot is set to 0")
        if abs((hist_data.iloc[-1]['P_E'] - self.pivot) / self.pivot) >= self.change_threshold:
            return True
        return False

    def apply_to_portfolio(self, **kwargs):
        df_nifty = kwargs.get("df")
        curr_date = kwargs.get("curr_date")
        p: Portfolio = kwargs.get("portfolio")
        # // weights will be recalculated based on parameters.
        weights = self.get_asset_weights(df_nifty, curr_date)
        self.pivot = df_nifty.iloc[-1]['P_E']
        p.rebalance_by_weights(curr_date=curr_date, eq_weight=weights["eq_weight"],
                               debt_weight=weights["debt_weight"],
                               gold_weight=weights["gold_weight"],
                               cash_weight=weights["cash_weight"])

    def backtest(self, ticker_dao: TickerDAO, **kwargs) -> Report:
        try:
            back_test_start_date = kwargs.get('back_test_start_date')

            df_nifty = ticker_dao.read_all_data("NIFTY 50")
            df_nifty_pe = ticker_dao.read_all_pe_data("NIFTY 50")
            df_nifty = df_nifty.merge(df_nifty_pe, how="left", on="Date")
            df_nifty_init = get_df_between_dates(df_nifty, back_test_start_date, back_test_start_date + timedelta(5))
            back_test_start_date = df_nifty_init.iloc[0]['Date']
            nifty_on_start_date = df_nifty_init.iloc[0]

            self.pivot = nifty_on_start_date['P_E']

            weights = self.get_asset_weights(df_nifty, back_test_start_date)

            p: Portfolio = PortfolioBuilder() \
                .with_name("test_portfolio") \
                .with_initial_capital(100000) \
                .with_eq_weight(weights["eq_weight"]) \
                .with_debt_weight(weights["debt_weight"]) \
                .with_gold_weight(weights["gold_weight"]) \
                .with_cash_weight(weights["cash_weight"]) \
                .with_stocks(["NIFTY 50"]) \
                .with_debts(["SAVINGS_ACC"]) \
                .on_date(back_test_start_date) \
                .build()
            p.apply_strategy(self)
            # iterate over each historical day from the date mentioned in kwargs
            report: Report = Report()
            for index, row in df_nifty.iterrows():
                curr_date = row['Date']
                print(curr_date)
                if curr_date >= back_test_start_date:
                    report.track((curr_date, p.get_value_as_of_date(curr_date)))
                    # in each iteration check if the strategy constraints are met.
                    mask = (df_nifty['Date'] >= back_test_start_date.strftime("%d-%b-%Y")) & (
                            df_nifty['Date'] <= curr_date.strftime("%d-%b-%Y"))
                    df1 = df_nifty.loc[mask]
                    if self.check_if_constraints_are_matched(df1):
                        # // weights will be recalculated based on parameters.
                        weights = self.get_asset_weights(df_nifty, curr_date)
                        self.pivot = df1.iloc[-1]['P_E']
                        p.rebalance_by_weights(curr_date=curr_date, eq_weight=weights["eq_weight"],
                                               debt_weight=weights["debt_weight"],
                                               gold_weight=weights["gold_weight"], cash_weight=weights["cash_weight"])
                        message = f"Total Invested: ${p.total_invested()}, " \
                                  f"Current Value: ${p.get_value_as_of_date(curr_date)} \r\n " \
                                  f"eq: {p.get_asset_weight(AssetType.EQUITY, curr_date)} " \
                                  f"debt: {p.get_asset_weight(AssetType.DEBT, curr_date)} " \
                                  f"gold: {p.get_asset_weight(AssetType.GOLD, curr_date)} " \
                                  f"cash: {p.get_asset_weight(AssetType.CASH, curr_date)}"
                        current_pe = (df_nifty.loc[df_nifty['Date'] == curr_date])['P_E'].iloc[0]
                        p.add_rebalance_logs(f"Portfolio rebalanced on {curr_date} pe:{current_pe} \n + ${message}")
            report.add_portfolio(p)
            return report
        except PortfolioCreationException:
            logger.error("Backtest failed because portfolio could not be created")
        except Exception as e:
            logger.error(f"Backtest failed: {e}")

    @staticmethod
    def get_asset_weights(df_nifty, curr_date):
        result = {}
        mask = (df_nifty['Date'] >= (curr_date - timedelta(days=365 * 5)).strftime("%d-%b-%Y")) & (
                df_nifty['Date'] <= curr_date.strftime("%d-%b-%Y"))
        df_nifty_slice = df_nifty.loc[mask]
        cur_pe = df_nifty_slice.iloc[-1]['P_E']
        df_nifty_slice = df_nifty_slice.sort_values("P_E", ascending=True, inplace=False)
        df_nifty_slice["P_E_Range"] = pd.cut(df_nifty_slice["P_E"],
                                             bins=(int(df_nifty_slice["P_E"].max()) - int(
                                                 df_nifty_slice["P_E"].min() + 1)), precision=2,
                                             ordered=True)
        new_pd = df_nifty_slice["P_E_Range"].value_counts() / df_nifty_slice["P_E"].count()
        new_pd = new_pd.to_frame(name="Probablity")
        new_pd.sort_index(inplace=True)
        new_pd["P_E_Range"] = new_pd.index
        new_pd["Cumulative_Probablity"] = new_pd["Probablity"].cumsum()
        new_pd["Equity_Weightage"] = round(80 - (80 - 50) * new_pd["Cumulative_Probablity"], 2)
        new_pd["P_E_Range"] = new_pd["P_E_Range"].astype("string")
        for index, row in new_pd.iterrows():
            cat_min = float(row["P_E_Range"].split(",")[0].split("(")[1])
            cat_max = float(row["P_E_Range"].split(",")[1].split("]")[0])
            if cat_min < cur_pe <= cat_max:
                result["eq_weight"] = row["Equity_Weightage"] / 100

        if "eq_weight" not in result.keys():
            raise Exception("Could not determine equity weight")

        # TODO: get debt weight
        result["debt_weight"] = (1 - result["eq_weight"])
        # TODO: get gold weight
        result["gold_weight"] = 0
        # get cash weight
        result["cash_weight"] = 1 - result["eq_weight"] - result["gold_weight"] - result["debt_weight"]
        return result
