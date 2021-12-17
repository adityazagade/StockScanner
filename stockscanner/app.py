import logging

from stockscanner.model.config import Config
from stockscanner.model.watchers.index_watcher import IndexWatcher
from stockscanner.model.watchers.change_watcher import ChangeWatcher


logger = logging.getLogger(__name__)

logger.info("App started")

# read configuration file
logger.info("Reading the configuration")
config = Config.load_config()

# init app
index_watcher = IndexWatcher(ticker="NIFTY 50", watch_freq=config["watch_freq"], db=config["db"],
                             hist_start_year=config["hist_start_year"])
logger.info("staring the index watcher")
index_watcher.start()

change_watcher = ChangeWatcher()
change_watcher.start()