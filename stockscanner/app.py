import logging

from stockscanner.model.config import Config
from stockscanner.model.index_watcher import IndexWatcher
from stockscanner.model.change_watcher import ChangeWatcher

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.INFO)

logger.info("App started")

# read configuration file
logger.info("Reading the configuration")
config = Config.load_config()

# init app
index_watcher = IndexWatcher(ticker="NIFTY", watch_freq=config["watch_freq"], db=config["db"])
index_watcher.start()

change_watcher = ChangeWatcher()
change_watcher.start()
