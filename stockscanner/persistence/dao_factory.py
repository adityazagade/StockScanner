from stockscanner.persistence.dao import TickerDAO
from stockscanner.persistence.fs.fs_impl import TickerFileSystemDB
from stockscanner.persistence.sqlite.sqlite_impl import SqliteTickerDaoImpl


def get_ticker_dao(db, **kwargs) -> TickerDAO:
    if db == "fs":
        return TickerFileSystemDB()
    if db == "sqlite3":
        return SqliteTickerDaoImpl(**kwargs)
