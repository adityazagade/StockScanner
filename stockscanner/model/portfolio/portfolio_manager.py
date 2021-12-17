from typing import List

from stockscanner.model.config import Config
from stockscanner.model.portfolio.portfolio import Portfolio
from stockscanner.persistence import dao_factory


class PortfolioManager:
    manager = None

    def __init__(self, config) -> None:
        self.pf_dao: PortfolioDAO = dao_factory.get_portfolio_dao(config["db"])
        self.portfolios: List[Portfolio] = self.pf_dao.load_all_portfolios()

    @classmethod
    def get_instance(cls):
        config = Config.load_config()
        if PortfolioManager.manager is None:
            PortfolioManager.manager = PortfolioManager(config)
        return PortfolioManager.manager

    def get_portfolio_following_strategy(self, sname: str):
        result: List[Portfolio] = []
        for p in self.portfolios:
            if p.get_strategy().name == sname:
                result.append(p)
        return result
