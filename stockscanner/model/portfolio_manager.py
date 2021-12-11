from stockscanner.persistence import dao_factory

class PortfolioManager:
    def __init__(self, config) -> None:
        self.pf_dao: PortfolioDAO = dao_factory.get_portfolio_dao(config["db"])
        self.portfolios = self.pf_dao.load_all_portfolios()