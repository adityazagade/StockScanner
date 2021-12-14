from stockscanner.model.config import Config
from stockscanner.persistence.dao import TickerDAO


class DAOManager:
    manager = None

    def __init__(self, db) -> None:
        self.dao = {}
        from stockscanner.persistence import dao_factory
        self.dao["ticker_dao"] = (dao_factory.get_ticker_dao(db, check_same_thread=False))

    def get_dao_for_ticker(self) -> TickerDAO:
        return self.dao["ticker_dao"]

    @classmethod
    def get_instance(cls):
        config = Config.load_config()
        if DAOManager.manager is None:
            DAOManager.manager = DAOManager(config["db"])
        return DAOManager.manager
