import logging
from abc import ABC, abstractmethod
from datetime import timedelta

import pandas as pd

from stockscanner.model.asset import Equity, Debt, Cash
from stockscanner.model.report import Report

logger = logging.getLogger(__name__)


def get_df_between_dates(df, start_date, end_date):
    mask = (df['Date'] >= start_date.strftime("%d-%b-%Y")) & (df['Date'] < (end_date).strftime("%d-%b-%Y"))
    return df.loc[mask]


class Strategy(ABC):
    def __init__(self):
        self.name = None

    @abstractmethod
    def check_if_constraints_are_matched(self, hist_data, **kwargs) -> bool:
        pass

    @abstractmethod
    def backtest(self, df, **kwargs) -> Report:
        pass


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

    def backtest(self, ticker_dao, **kwargs) -> Report:
        back_test_start_date = kwargs.get('back_test_start_date')

        # calculate weight for start for each assets. assume 0.5 equity and 0.5 cash
        initial_amount = 100000
        eq_weight = 0.5
        debt_weight = 0
        cash_weight = 0.5
        gold_wight = 0

        # create portfolio based on weights
        from stockscanner.model.portfolio import Portfolio
        p: Portfolio = Portfolio("test_portfolio")

        # read nifty hist data
        df_nifty = None
        pivot = 0
        try:
            df_nifty = ticker_dao.read_all_data("NIFTY 50")
            df_nifty_init = get_df_between_dates(df_nifty, back_test_start_date, back_test_start_date + timedelta(5))
            back_test_start_date = df_nifty_init.iloc[0]['Date']
            nifty_on_start_date = df_nifty_init.iloc[0]
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

        try:
            cash_value = cash_weight * initial_amount
            cash = Cash(cash_value)
            p.add_asset(cash)
        except Exception as e:
            logger.error(f"Error adding cash part to portfolio while back-testing {e}")

        p.apply_strategy(self)
        # iterate over each historical day from the date mentioned in kwargs
        for index, row in df_nifty.iterrows():
            curr_date = row['Date']
            print(curr_date)
            if curr_date >= back_test_start_date:
                # in each iteration check if the strategy constraints are met.
                mask = (df_nifty['Date'] >= back_test_start_date.strftime("%d-%b-%Y")) & (
                        df_nifty['Date'] <= curr_date.strftime("%d-%b-%Y"))
                df1 = df_nifty.loc[mask]
                if self.check_if_constraints_are_matched(df1, pivot=pivot):
                    # // wieights will be recalulated based on parameters.
                    pivot = df1.iloc[-1]['Close']
                    # if the constraints are met, then call rebalance on portfolio.
                    p.do_rebalance(curr_date=curr_date, eq_weight=eq_weight, debt_weight=debt_weight,
                                   gold_wight=gold_wight, cash_weight=cash_weight)
                    p.add_rebalance_logs(f"Portfolio rebalanced on {curr_date}")

        return Report(p)
