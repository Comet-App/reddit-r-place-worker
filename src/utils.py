import logging
import os
import re
import stem.process


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
    # TODO: Check if streamhandler logs exists and add only is handler is not present
    log_stream = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s.%(funcName)s: %(message)s",
    )
    log_stream.set_name("stream_handler")
    log_stream.setFormatter(formatter)
    logger.addHandler(log_stream)
    return logger


def launch_tor(port=9050):
    tor_process = stem.process.launch_tor_with_config(
        config={
            "SocksPort": str(port),
        },
        init_msg_handler=lambda line: print(line)
        if re.search("Bootstrapped", line)
        else False,
    )
    return tor_process


TOR_PROXY = "socks5://127.0.0.1:9050"
