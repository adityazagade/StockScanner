from stockscanner.persistence.dao import TickerDAO, TickerFileSystemDB


def get_ticker_dao(db) -> TickerDAO:
    if db == "fs":
        return TickerFileSystemDB()
