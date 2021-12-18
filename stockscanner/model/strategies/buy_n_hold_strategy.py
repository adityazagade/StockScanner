import logging
from datetime import timedelta

import pandas as pd

from stockscanner.model.exceptions.exceptions import PortfolioCreationException
from stockscanner.model.portfolio.portfolio import Portfolio
from stockscanner.model.portfolio.portfolio_builder import PortfolioBuilder
from stockscanner.model.reporting.report import Report
from stockscanner.model.strategies.strategy import Strategy
from stockscanner.persistence.dao import TickerDAO
from stockscanner.utils.DateUtils import get_df_between_dates

logger = logging.getLogger(__name__)


class BuyAndHold(Strategy):
    def __init__(self) -> None:
        super().__init__()
        self.name = "BuyAndHold"

    def check_if_constraints_are_matched(self, hist_data: pd.DataFrame, **kwargs) -> bool:
        return False

    def apply_to_portfolio(self, **kwargs):
        kwargs.get("df")
        curr_date = kwargs.get("curr_date")
        p: Portfolio = kwargs.get("portfolio")
        # // weights will be recalculated based on parameters.
        weights = self.get_asset_weights()
        p.rebalance_by_weights(curr_date=curr_date, eq_weight=weights["eq_weight"],
                               debt_weight=weights["debt_weight"],
                               gold_weight=weights["gold_weight"],
                               cash_weight=weights["cash_weight"])

    def backtest(self, ticker_dao: TickerDAO, **kwargs) -> Report:
        try:
            back_test_start_date = kwargs.get('back_test_start_date')

            p = PortfolioBuilder() \
                .with_name("test_portfolio") \
                .with_initial_capital(100000) \
                .with_eq_weight(1) \
                .with_debt_weight(0) \
                .with_gold_weight(0) \
                .with_cash_weight(0) \
                .with_stocks(["NIFTY 50"]) \
                .on_date(back_test_start_date) \
                .build()

            df_nifty = ticker_dao.read_all_data("NIFTY 50")
            df_nifty_pe = ticker_dao.read_all_pe_data("NIFTY 50")
            df_nifty = df_nifty.merge(df_nifty_pe, how="left", on="Date")
            df_nifty_init = get_df_between_dates(df_nifty, back_test_start_date,
                                                 back_test_start_date + timedelta(5))
            back_test_start_date = df_nifty_init.iloc[0]['Date']

            p.apply_strategy(self)
            # iterate over each historical day from the date mentioned in kwargs
            report: Report = Report()
            for index, row in df_nifty.iterrows():
                curr_date = row['Date']
                logger.debug(curr_date)
                if curr_date >= back_test_start_date:
                    report.track((curr_date, p.get_value_as_of_date(curr_date)))
            report.add_portfolio(p)
            return report
        except PortfolioCreationException:
            logger.error("Backtest failed because portfolio could not be created")
        except Exception as e:
            logger.error(f"Backtest failed: {e}")

    @staticmethod
    def get_asset_weights():
        return {
            "eq_weight": 1,
            "debt_weight": 0,
            "gold_weight": 0,
            "cash_weight": 0
        }
