import logging
import threading

from stockscanner.model.index_watcher import IndexWatcher
from stockscanner.model.change_watcher import ChangeWatcher

logger = logging.getLogger(__name__)
logger.info("I would crawl the data at 17:10")

# read configuration file

# init app
index_watcher = IndexWatcher()
index_watcher_thread = threading.Thread(target=index_watcher.run)
index_watcher_thread.start()

change_watcher = ChangeWatcher()
change_watcher_thread = threading.Thread(target=change_watcher.run)
change_watcher_thread.start()