import logging


def init_log():
    root_logger = logging.getLogger()
    root_logger.setLevel(level=logging.INFO)
    logging.basicConfig(level=logging.INFO)


init_log()
