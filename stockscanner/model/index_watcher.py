import logging
import time
import bs4

from datetime import date
from threading import Thread

from stockscanner.persistence import dao_factory
from stockscanner.persistence.dao import DAO
from stockscanner.utils import HttpUtils, Constants

logger = logging.getLogger(__name__)


class IndexWatcher(Thread):
    def __init__(self, ticker, watch_freq, db):
        super().__init__()
        self.watch_freq = watch_freq * 60
        self.ticker = ticker
        self.index_dao: DAO = dao_factory.get_index_dao(db)

    def run(self):
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
            params = {
                "indexType": "NIFTY 50",
                "fromDate": date.today().strftime("%d-%m-%Y"),
                "toDate": date.today().strftime("%d-%m-%Y")
            }
            url = Constants.BASE_URL_NSE1 + "/products/dynaContent/equities/indices/historicalindices.jsp"
            response = HttpUtils.do_get(url=url, query_parameters=params)
            soup = bs4.BeautifulSoup(response, "lxml")
            # extract from soup now
            OHLC_table = soup.find("div", {"id": "csvContentDiv"}).text
            lst = OHLC_table.split(":")
            headers = lst[0]
            # remove header and last entry(which is empty)
            lst.pop(0)
            lst.pop()
            ohlc_dict = {}
            for entry in lst:
                tmp = entry.split(",")
                for index, item in enumerate(tmp):
                    key = headers.split(",")[index].strip('"').strip()
                    ohlc_dict[key] = item
            # once extracted, need to persist
            self.index_dao.save(ohlc_dict)
        except Exception as e:
            logger.error(e)

    def download_historical_data(self):
        pass
