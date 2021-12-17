import time
from threading import Thread
from typing import List

from stockscanner.model.portfolio.portfolio import Portfolio
from stockscanner.model.portfolio.portfolio_manager import PortfolioManager
from stockscanner.model.strategies.strategy import Strategy


class ChangeWatcher(Thread):
    def __init__(self):
        super().__init__()

    def run(self):
        time.sleep(30)

        # 1. load the date from the file system using the Ticker_DAO
        from stockscanner.persistence.dao_manager import DAOManager
        from stockscanner.model.strategies.strategy_manager import StrategyManager

        dao = DAOManager.get_instance().get_dao_for_ticker()
        df_nifty = dao.read_all_data("NIFTY 50")
        df_nifty_pe = dao.read_all_pe_data("NIFTY 50")
        df_nifty = df_nifty.merge(df_nifty_pe, how="left", on="Date")

        sm = StrategyManager.get_instance()
        strategies: List[Strategy] = sm.get_all_strategies()
        for s in strategies:
            from datetime import date
            curr_date = date.today()
            if s.check_if_constraints_are_matched(df_nifty):
                portfolios: List[Portfolio] = PortfolioManager.get_instance().get_portfolio_following_strategy(s.name)
                for portfolio in portfolios:
                    s.apply_to_portfolio(df=df_nifty, curr_date=curr_date, portfolio=portfolio)