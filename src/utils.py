import logging
import os


def get_log_level(log_level):
    log_level = log_level.upper()
    if log_level == "CRITICAL":
        return logging.CRITICAL
    elif log_level == "ERROR":
        return logging.ERROR
    elif log_level == "WARNING":
        return logging.WARN
    elif log_level == "DEBUG":
        return logging.DEBUG
    else:
        return logging.INFO


def get_logger(logger_name: str = "", log_level=None):
    ENV_LOG_LEVEL = os.getenv("LOG_LEVEL") or "DEBUG"

    if log_level is None:
        log_level = ENV_LOG_LEVEL
    log_level = get_log_level(log_level)
    logger = logging.getLogger(logger_name)
    logger.setLevel(log_level)

    # Get all handlers in the log
    log_stream = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s.%(funcName)s: %(message)s",
    )
    log_stream.set_name("stream_handler")
    log_stream.setFormatter(formatter)
    logger.addHandler(log_stream)
    return logger
