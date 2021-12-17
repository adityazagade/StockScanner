from datetime import timedelta

import pandas as pd

from stockscanner.model.portfolio.asset import Equity, Debt, Cash
from stockscanner.model.portfolio.portfolio import Portfolio
from stockscanner.model.reporting.report import Report
from stockscanner.model.strategies.strategy import Strategy, logger
from stockscanner.utils.DateUtils import get_df_between_dates
from stockscanner.persistence.dao import TickerDAO


class MarketMovementBasedAllocation(Strategy):
    def __init__(self, percent_change) -> None:
        super().__init__()
        self.name = "MarketMovementBasedAllocation"
        self.change_threshold = percent_change / 100

    def check_if_constraints_are_matched(self, hist_data: pd.DataFrame, **kwargs) -> bool:
        pivot = kwargs.get("pivot")
        if abs((hist_data.iloc[-1]['Close'] - pivot) / pivot) >= self.change_threshold:
            return True
        return False

    def apply_to_portfolio(self, **kwargs):
        df_nifty = kwargs.get("df")
        curr_date = kwargs.get("curr_date")
        portfolio: Portfolio = kwargs.get("portfolio")
        # // weights will be recalculated based on parameters.
        eq_weight = self.get_eq_weight(df_nifty, curr_date)
        cash_weight = 1 - eq_weight
        self.pivot = df_nifty.iloc[-1]['Close']
        current_pe = (df_nifty.loc[df_nifty['Date'] == curr_date])['P_E'].iloc[0]
        portfolio.rebalance_by_weights(curr_date=curr_date, current_pe=current_pe, eq_weight=eq_weight,
                                       cash_weight=cash_weight)

    def backtest(self, ticker_dao: TickerDAO, **kwargs) -> Report:
        back_test_start_date = kwargs.get('back_test_start_date')

        # create portfolio based on weights
        from stockscanner.model.portfolio.portfolio import Portfolio
        p: Portfolio = Portfolio("test_portfolio")

        # read nifty hist data
        df_nifty = None
        pivot = 0
        # calculate weight for start for each assets. assume 0.5 equity and 0.5 cash
        initial_amount = 100000
        eq_weight = 0.5
        gold_wight = 0
        try:
            df_nifty = ticker_dao.read_all_data("NIFTY 50")
            df_nifty_pe = ticker_dao.read_all_pe_data("NIFTY 50")
            df_nifty = df_nifty.merge(df_nifty_pe, how="left", on="Date")
            df_nifty_init = get_df_between_dates(df_nifty, back_test_start_date, back_test_start_date + timedelta(5))
            back_test_start_date = df_nifty_init.iloc[0]['Date']
            nifty_on_start_date = df_nifty_init.iloc[0]
            eq_weight = self.get_eq_weight(df_nifty=df_nifty, curr_date=back_test_start_date)
            eq_value = eq_weight * initial_amount
            eq_price = nifty_on_start_date['Close']
            pivot = eq_price
            eq_quantity = eq_value / eq_price
            eq = Equity()
            eq.add(symbol="NIFTY 50", date=back_test_start_date, quantity=eq_quantity, price=eq_price)
            p.add_asset(eq)
        except Exception as e:
            logger.error(f"Error adding equity part to portfolio while back-testing {e}")
            raise Exception("This should not have happened. Mark back testing as failure")

        debt_weight = 0
        try:
            # read liquid bees hist data
            df_lq_bees = ticker_dao.read_all_data("LIQUIDBEES")
            df_lq_bees = get_df_between_dates(df_lq_bees, back_test_start_date, back_test_start_date + timedelta(5))
            liquid_bees_on_start_date = df_lq_bees.iloc[0]
            debt_value = debt_weight * initial_amount
            debt_price = liquid_bees_on_start_date['Close']
            debt_quantity = debt_value / debt_price
            debt = Debt()
            debt.add(symbol="LIQUIDBEES", date=back_test_start_date, quantity=debt_quantity, price=debt_price)
            p.add_asset(debt)
        except Exception as e:
            logger.error(f"Error adding debt part to portfolio while back-testing {e}")

        cash_weight = 1 - eq_weight
        try:
            cash_value = cash_weight * initial_amount
            cash = Cash(cash_value)
            p.add_asset(cash)
        except Exception as e:
            logger.error(f"Error adding cash part to portfolio while back-testing {e}")

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
                if self.check_if_constraints_are_matched(df1, pivot=pivot):
                    # // weights will be recalculated based on parameters.
                    eq_weight = self.get_eq_weight(df_nifty, curr_date)
                    cash_weight = 1 - eq_weight
                    pivot = df1.iloc[-1]['Close']
                    p.rebalance_by_weights(curr_date=curr_date, eq_weight=eq_weight, debt_weight=debt_weight,
                                           gold_wight=gold_wight, cash_weight=cash_weight)
                    message = f"Total Invested: ${p.total_invested()}, Current Value: ${p.get_value_as_of_date(curr_date)} \r\n eq: {p.get_eq_weight(curr_date)} debt: {p.get_debt_weight(curr_date)} gold: {p.get_gold_weight(curr_date)} cash: {p.get_cash_weight(curr_date)}"
                    current_pe = (df_nifty.loc[df_nifty['Date'] == curr_date])['P_E'].iloc[0]
                    p.add_rebalance_logs(f"Portfolio rebalanced on {curr_date} pe:{current_pe} \n + ${message}")
        report.add_portfolio(p)
        return report

    def get_eq_weight(self, df_nifty, curr_date) -> float:
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
                return row["Equity_Weightage"] / 100
        raise Exception("Could not determine equity weight")