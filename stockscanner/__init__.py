import logging

from stockscanner.model.config import Config


def get_log_level(level):
    if level == "critical":
        return logging.CRITICAL
    elif level == "fatal":
        return logging.FATAL
    elif level == "error":
        return logging.ERROR
    elif level == "warning":
        return logging.WARNING
    elif level == "warn":
        return logging.WARN
    elif level == "info":
        return logging.INFO
    elif level == "debug":
        return logging.DEBUG
    else:
        return logging.NOTSET


def init_log(config):
    root_logger = logging.getLogger()
    root_logger.setLevel(level=get_log_level(config["logging"]["log_level"]))
    logging.basicConfig(level=get_log_level(config["logging"]["log_level"]))


init_log(Config.load_config())
