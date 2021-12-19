import logging
from datetime import timedelta, date, datetime

from stockscanner.model.asset.asset_type import AssetType
from stockscanner.model.exceptions.exceptions import PortfolioCreationException
from stockscanner.model.portfolio.portfolio import Portfolio
from stockscanner.model.portfolio.portfolio_builder import PortfolioBuilder
from stockscanner.model.reporting.report import Report
from stockscanner.model.strategies.strategy import Strategy
from stockscanner.persistence.dao import TickerDAO
from stockscanner.utils.DateUtils import get_df_between_dates

logger = logging.getLogger(__name__)

import enum


class SipFrequency(enum.Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"

    @staticmethod
    def does_value_exist(value):
        freq_set = [item.value for item in SipFrequency]  # [4, 5, 6]
        return value in freq_set

    @staticmethod
    def get_by_value(val):
        for freq in SipFrequency:
            if freq.value == val:
                return freq


class SIP(Strategy):

    def init(self, strategy_config: dict):
        if "sip_start_date" in strategy_config.keys():
            self.sip_start_date = datetime.strptime(strategy_config["sip_start_date"], '%d-%m-%Y').date()
        if "sip_amount" in strategy_config.keys():
            if strategy_config["sip_amount"] <= 0:
                raise Exception("Strategy initiation failed. Amount lte 0")
            self.sip_amount = strategy_config["sip_amount"]
        if "sip_frequency" in strategy_config.keys():
            self.sip_frequency = SipFrequency.get_by_value(strategy_config["sip_frequency"])

    def __init__(self, sip_start_date: date = date.today(), sip_amount: int = 5000,
                 sip_frequency: SipFrequency = SipFrequency.MONTHLY) -> None:
        super().__init__()

        if sip_amount <= 0:
            raise Exception("Strategy initiation failed. Amount lte 0")

        self.name = "SIP"
        self.sip_start_date = sip_start_date
        self.sip_frequency = sip_frequency
        self.sip_amount = sip_amount

    def check_if_constraints_are_matched(self, **kwargs) -> bool:
        curr_date: date = kwargs.get("date")
        if self.sip_frequency == SipFrequency.DAILY:
            return curr_date >= self.sip_start_date
        elif self.sip_frequency == SipFrequency.WEEKLY:
            return (curr_date >= self.sip_start_date) and (self.sip_start_date.weekday() == curr_date.weekday())
        elif self.sip_frequency == SipFrequency.MONTHLY:
            return (curr_date >= self.sip_start_date) and (self.sip_start_date.day == curr_date.day)

    def apply_to_portfolio(self, **kwargs):
        curr_date = kwargs.get("date")
        p: Portfolio = kwargs.get("portfolio")
        p.add_equities_by_amount(self.sip_amount, curr_date)

    def backtest(self, ticker_dao: TickerDAO, **kwargs) -> Report:
        try:
            back_test_start_date = kwargs.get('back_test_start_date')

            df_nifty = ticker_dao.read_all_data("NIFTY 50")
            df_nifty_pe = ticker_dao.read_all_pe_data("NIFTY 50")
            df_nifty = df_nifty.merge(df_nifty_pe, how="left", on="Date")
            df_nifty_init = get_df_between_dates(df_nifty, back_test_start_date, back_test_start_date + timedelta(5))
            back_test_start_date = df_nifty_init.iloc[0]['Date']

            p: Portfolio = PortfolioBuilder() \
                .with_name("test_portfolio") \
                .with_initial_capital(1) \
                .with_eq_weight(1) \
                .with_debt_weight(0) \
                .with_gold_weight(0) \
                .with_cash_weight(0) \
                .with_stocks(["NIFTY 50"]) \
                .on_date(self.sip_start_date) \
                .build()
            p.apply_strategy(self)

            report: Report = Report()

            # iterate over each historical day from the date mentioned in kwargs
            for index, row in df_nifty.iterrows():
                curr_date = row['Date']
                print(curr_date)
                if curr_date >= back_test_start_date:
                    if curr_date < self.sip_start_date:
                        # report.track((curr_date, 0))
                        pass
                    else:
                        # in each iteration check if the strategy constraints are met.
                        if self.check_if_constraints_are_matched(date=curr_date):
                            # // weights will be recalculated based on parameters.
                            p.add_equities_by_amount(self.sip_amount, curr_date)
                            message = f"Total Invested: ${p.total_invested()}, " \
                                      f"Current Value: ${p.get_value_as_of_date(curr_date)} \r\n " \
                                      f"eq: {p.get_asset_weight(AssetType.EQUITY, curr_date)} " \
                                      f"debt: {p.get_asset_weight(AssetType.DEBT, curr_date)} " \
                                      f"gold: {p.get_asset_weight(AssetType.GOLD, curr_date)} " \
                                      f"cash: {p.get_asset_weight(AssetType.CASH, curr_date)}"
                            current_pe = (df_nifty.loc[df_nifty['Date'] == curr_date])['P_E'].iloc[0]
                            p.add_rebalance_logs(f"Portfolio rebalanced on {curr_date} pe:{current_pe} \n + ${message}")
                        report.track((curr_date, p.get_value_as_of_date(curr_date)))
            report.add_portfolio(p)
            return report
        except PortfolioCreationException:
            logger.error("Backtest failed because portfolio could not be created")
        except Exception as e:
            logger.error(f"Backtest failed: {e}")

    @staticmethod
    def get_asset_weights():
        result = {"eq_weight": 1}
        result[""] = (1 - result["eq_weight"])
        result["gold_weight"] = 0
        result["cash_weight"] = 1 - result["eq_weight"] - result["gold_weight"] - result["debt_weight"]
        return result
