from threading import Thread


class ChangeWatcher(Thread):
    def __init__(self):
        super().__init__()

    def run(self):
        pass
        # 1. load the date from the file system using the Ticker_DAO
        # 2. When there is a
