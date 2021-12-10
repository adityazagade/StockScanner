import logging
import threading
import time
import bs4

from datetime import date, timedelta
from threading import Thread

from stockscanner.persistence import dao_factory
from stockscanner.persistence.dao import DAO
from stockscanner.utils import HttpUtils, Constants

logger = logging.getLogger(__name__)


class IndexWatcher(Thread):
    def __init__(self, ticker, watch_freq, db, hist_start_year):
        super().__init__()
        self.hist_start_year = hist_start_year
        self.watch_freq = watch_freq * 60
        self.ticker = ticker
        self.index_dao: DAO = dao_factory.get_index_dao(db)

    def run(self) -> None:
        historical_data_exists = self.index_dao.schema_exists()
        # 1. Check if the File/Table exists. If yes, don't pull the historical data. Else pull it and persist
        if not historical_data_exists:
            # download historical data
            self.download_historical_data()
        # 2. Pull the data from the NSE Website for today. Save to DB.
        self.download_today_data()
        # 3. Sleep for configured time.
        time.sleep(self.watch_freq)

    def download_today_data(self):
        try:
            logger.info("Starting to download today's data...")
            self.download_data_between_dates(self.ticker, start_date=date.today(), end_date=date.today())
            logger.info("Starting to download today's data... Done")
        except Exception as e:
            logger.error(e)

    def download_historical_data(self):
        logger.info(f"${threading.current_thread()} Starting to download historical data...")
        try:
            self.write_headers()
            time.sleep(1)
            for i in range(self.hist_start_year, date.today().year + 1):
                if i % 4 == 0:
                    # leap year. Cannot download data for more than 365 days. So split req into two parts
                    self.download_data_between_dates(self.ticker, start_date=date(i, 1, 1), end_date=date(i, 12, 30))
                    self.download_data_between_dates(self.ticker, start_date=date(i, 12, 31), end_date=date(i, 12, 31))
                else:
                    self.download_data_between_dates(self.ticker, start_date=date(i, 1, 1), end_date=date(i, 12, 31))
                logger.info(str(i) + "... done")
                logger.info("Sleep for 2 seconds...")
                time.sleep(2)  # sleep for 10 seconds
        except Exception as e:
            logger.error(e)

    def download_data_between_dates(self, ticker, start_date, end_date):
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
                # ohlc_dict = {}
                for entry in lst:
                    self.index_dao.save("\n" + entry)
                # tmp = entry.split(",")
                # for index, item in enumerate(tmp):
                #     key = headers.split(",")[index].strip('"').strip()
                #     ohlc_dict[key] = item
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
        self.index_dao.save(headers)


if __name__ == '__main__':
    pass
