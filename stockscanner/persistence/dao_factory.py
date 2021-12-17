from stockscanner.persistence.dao import TickerDAO, PortfolioDAO, StrategyDAO
from stockscanner.persistence.fs.fs_impl import TickerFileSystemDB, FSPortfolioDaoImpl, FSStrategyDaoImpl
from stockscanner.persistence.sqlite.sqlite_impl import SqliteTickerDaoImpl, SqliteStrategyDaoImpl, \
    SqlitePortfolioDaoImpl


def get_ticker_dao(db, **kwargs) -> TickerDAO:
    if db == "fs":
        return TickerFileSystemDB()
    if db == "sqlite3":
        return SqliteTickerDaoImpl(**kwargs)


def get_portfolio_dao(db, **kwargs) -> PortfolioDAO:
    if db == "fs":
        return FSPortfolioDaoImpl()
    if db == "sqlite3":
        return SqlitePortfolioDaoImpl(**kwargs)


def get_strategy_dao(db, **kwargs) -> StrategyDAO:
    if db == "fs":
        return FSStrategyDaoImpl()
    if db == "sqlite3":
        return SqliteStrategyDaoImpl(**kwargs)
