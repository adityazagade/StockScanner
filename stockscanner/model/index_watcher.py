import logging
import threading
import time
import bs4

from datetime import date, timedelta
from threading import Thread

from stockscanner.persistence import dao_factory
from stockscanner.persistence.dao import TickerDAO
from stockscanner.utils import HttpUtils, Constants

logger = logging.getLogger(__name__)


class IndexWatcher(Thread):
    def __init__(self, ticker, watch_freq, db, hist_start_year):
        super().__init__()
        self.hist_start_year = hist_start_year
        self.watch_freq = watch_freq * 60
        self.ticker = ticker
        self.ticker_dao: TickerDAO = dao_factory.get_ticker_dao(db)

    def run(self) -> None:
        # 1. pull hist data
        self.download_historical_ohlc_data()
        self.download_historical_pe_data()
        # 2. Pull the data from the NSE Website for yesterday. Save to DB.
        self.download_today_ohlc_data()
        self.download_today_pe_data()
        # 3. Sleep for configured time.
        # time.sleep(self.watch_freq)

    def download_today_ohlc_data(self):
        try:
            logger.info("Starting to download yesterday's data...")
            d = (date.today() - timedelta(1))
            self.download_ohlc_data_between_dates(self.ticker, start_date=d, end_date=d)
            logger.info("Starting to download today's data... Done")
        except Exception as e:
            logger.error(e)

    def download_historical_ohlc_data(self):
        historical_data_exists = self.ticker_dao.ohlc_schema_exists(self.ticker)
        if not historical_data_exists:
            logger.info(f"{threading.current_thread()} Starting to download historical data...")
            try:
                self.write_headers()
                time.sleep(1)
                for i in range(self.hist_start_year, date.today().year + 1):
                    if i % 4 == 0:
                        # leap year. Cannot download data for more than 365 days. So split req into two parts
                        self.download_ohlc_data_between_dates(self.ticker, start_date=date(i, 1, 1),
                                                              end_date=date(i, 12, 30))
                        self.download_ohlc_data_between_dates(self.ticker, start_date=date(i, 12, 31),
                                                              end_date=date(i, 12, 31))
                    else:
                        self.download_ohlc_data_between_dates(self.ticker, start_date=date(i, 1, 1),
                                                              end_date=date(i, 12, 31))
                    logger.info(str(i) + "... done")
                    logger.info("Sleep for 2 seconds...")
                    time.sleep(2)  # sleep for 10 seconds
            except Exception as e:
                logger.error(e)

    def download_ohlc_data_between_dates(self, ticker, start_date, end_date):
        try:
            params = {
                "indexType": ticker,
                "fromDate": start_date.strftime("%d-%m-%Y"),
                "toDate": end_date.strftime("%d-%m-%Y")
            }
            url = Constants.BASE_URL_NSE1 + "/products/dynaContent/equities/indices/historicalindices.jsp"
            response = HttpUtils.do_get(url=url, query_parameters=params)
            soup = bs4.BeautifulSoup(response, "lxml")
            # extract from soup now
            OHLC_table_div = soup.find("div", {"id": "csvContentDiv"})
            if OHLC_table_div:
                lst = OHLC_table_div.text.split(":")
                headers = lst[0]
                # remove header and last entry(which is empty)
                lst.pop(0)
                lst.pop()
                for entry in lst:
                    self.ticker_dao.save(self.ticker, "\n" + entry)
            else:
                logger.warning("Unable to get data for range " + str(start_date) + "-" + str(end_date))
        except Exception as e:
            logger.error(e)

    def write_headers(self):
        # i know for this date the data will come. I just need headers.dates don't matter
        start_date = date(2010, 1, 4)
        end_date = date(2010, 1, 4)
        params = {
            "indexType": self.ticker,
            "fromDate": start_date.strftime("%d-%m-%Y"),
            "toDate": end_date.strftime("%d-%m-%Y")
        }
        url = Constants.BASE_URL_NSE1 + "/products/dynaContent/equities/indices/historicalindices.jsp"
        response = HttpUtils.do_get(url=url, query_parameters=params)
        soup = bs4.BeautifulSoup(response, "lxml")
        # extract from soup now
        OHLC_table_div = soup.find("div", {"id": "csvContentDiv"})
        lst = OHLC_table_div.text.split(":")
        headers = lst[0]
        self.ticker_dao.save(self.ticker, headers)

    def download_historical_pe_data(self):
        historical_data_exists = self.ticker_dao.pe_schema_exists(self.ticker)
        if not historical_data_exists:
            logger.info(f"Starting to download historical pe data...")
            try:
                self.write_pe_headers()
                time.sleep(1)
                for i in range(self.hist_start_year, date.today().year + 1):
                    if i % 4 == 0:
                        # leap year. Cannot download data for more than 365 days. So split req into two parts
                        self.download_pe_data_between_dates(self.ticker, start_date=date(i, 1, 1),
                                                            end_date=date(i, 12, 30))
                        self.download_pe_data_between_dates(self.ticker, start_date=date(i, 12, 31),
                                                            end_date=date(i, 12, 31))
                    else:
                        self.download_pe_data_between_dates(self.ticker, start_date=date(i, 1, 1),
                                                            end_date=date(i, 12, 31))
                    logger.info(str(i) + "... done")
                    logger.info("Sleep for 2 seconds...")
                    time.sleep(2)  # sleep for 10 seconds
            except Exception as e:
                logger.error(e)

    def download_today_pe_data(self):
        try:
            logger.info("Starting to download yesterday's pe data...")
            d = (date.today() - timedelta(1))
            self.download_pe_data_between_dates(self.ticker, start_date=d, end_date=d)
            logger.info("Starting to download yesterday's pe data... Done")
        except Exception as e:
            logger.error(e)

    def download_pe_data_between_dates(self, ticker, start_date, end_date):
        try:
            params = {
                "indexName": ticker,
                "yield1": "undefined",
                "yield2": "undefined",
                "yield3": "undefined",
                "yield4": "all",
                "fromDate": start_date.strftime("%d-%m-%Y"),
                "toDate": end_date.strftime("%d-%m-%Y")
            }
            url = Constants.BASE_URL_NSE1 + "/products/dynaContent/equities/indices/historical_pepb.jsp"
            response = HttpUtils.do_get(url=url, query_parameters=params)
            soup = bs4.BeautifulSoup(response, "lxml")
            # extract from soup now
            OHLC_table_div = soup.find("div", {"id": "csvContentDiv"})
            if OHLC_table_div:
                lst = OHLC_table_div.text.split(":")
                headers = lst[0]
                # remove header and last entry(which is empty)
                lst.pop(0)
                lst.pop()
                for entry in lst:
                    self.ticker_dao.save_pe_data(self.ticker, "\n" + entry)
            else:
                logger.warning(
                    "Unable to get data for range " + str(params["start_date"]) + "-" + str(params["end_date"]))
        except Exception as e:
            logger.error(e)

    def write_pe_headers(self):
        # i know for this date the data will come. I just need headers.dates don't matter
        start_date = date(2020, 1, 6)
        end_date = date(2020, 1, 6)
        params = {
            "indexName": self.ticker,
            "yield1": "undefined",
            "yield2": "undefined",
            "yield3": "undefined",
            "yield4": "all",
            "fromDate": start_date.strftime("%d-%m-%Y"),
            "toDate": end_date.strftime("%d-%m-%Y")
        }
        url = Constants.BASE_URL_NSE1 + "/products/dynaContent/equities/indices/historical_pepb.jsp"
        response = HttpUtils.do_get(url=url, query_parameters=params)
        soup = bs4.BeautifulSoup(response, "lxml")
        # extract from soup now
        OHLC_table_div = soup.find("div", {"id": "csvContentDiv"})
        lst = OHLC_table_div.text.split(":")
        headers = lst[0]
        self.ticker_dao.save_pe_data(self.ticker, headers)


if __name__ == '__main__':
    pass
