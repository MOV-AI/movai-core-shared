"""
   Copyright (C) Mov.ai  - All Rights Reserved
   Unauthorized copying of this file, via any medium is strictly prohibited
   Proprietary and confidential

   Developers:
   - Dor Marcous (dor@mov.ai) - 2022
"""
import logging
import sys
from logging.handlers import TimedRotatingFileHandler
from envvars import (
    MOVAI_LOGFILE_VERBOSITY_LEVEL,
    MOVAI_STDOUT_VERBOSITY_LEVEL,
    MOVAI_GENERAL_VERBOSITY_LEVEL,
)

LOG_FORMATTER_DATETIME = "%Y-%m-%d %H:%M:%S"

LOG_FORMATTER = logging.Formatter(
    "[%(levelname)s][%(asctime)s][%(module)s][%(funcName)s][%(lineno)d]: %(message)s",
    datefmt=LOG_FORMATTER_DATETIME,
)

LOG_FORMATTER_HTTP = logging.Formatter(
    "[%(levelname)s][%(asctime)s][%(module)s][%(funcName)s][%(lineno)d]: %(message)s",
    datefmt=LOG_FORMATTER_DATETIME,
)


def _get_console_handler():
    """
    Set up the stdout handler
    """
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(LOG_FORMATTER)
    console_handler.setLevel(MOVAI_STDOUT_VERBOSITY_LEVEL)
    return console_handler


def _get_file_handler():
    """
    Set up the file handler
    """
    file_handler = TimedRotatingFileHandler(Log.LOG_FILE, when="midnight")
    file_handler.setFormatter(LOG_FORMATTER)
    file_handler.setLevel(MOVAI_LOGFILE_VERBOSITY_LEVEL)
    return file_handler


class Log:
    """
    A static class to help create logger instances
    """

    LOG_FILE = "movai.log"

    @staticmethod
    def set_log_file(name: str):
        """
        Set the name of the file we write the log
        """
        Log.LOG_FILE = name

    @staticmethod
    def get_logger(logger_name: str):
        """
        Get a logger instance
        """
        logger = logging.getLogger(logger_name)
        if MOVAI_STDOUT_VERBOSITY_LEVEL != logging.NOTSET:
            logger.addHandler(_get_console_handler())
        if MOVAI_LOGFILE_VERBOSITY_LEVEL != logging.NOTSET:
            logger.addHandler(_get_file_handler())
        logger.setLevel(MOVAI_GENERAL_VERBOSITY_LEVEL)
        logger.propagate = False
        return logger


class LogAdapter(logging.LoggerAdapter):
    """
    A LogAdapter used to expose the logger inside a callback, we should
    not need to use this adapter outside a callback.

    py_logger = Log.get_logger("logn ame")
    logger = LogAdapter(py_logger, tag1="value", tag2="value")

    Usage:
        logger.debug(<message>, <tagKey>=<tagValue>, <tagKey>=<tagValue>...)
        logger.info(<message>, <tagKey>=<tagValue>, <tagKey>=<tagValue>...)
        logger.warning(<message>, <tagKey>=<tagValue>, <tagKey>=<tagValue>...)
        logger.error(<message>, <tagKey>=<tagValue>, <tagKey>=<tagValue>...)
        logger.critical(<message>, <tagKey>=<tagValue>, <tagKey>=<tagValue>...)

    """

    def __init__(self, logger, **kwargs):
        super().__init__(logger, None)
        self._tags = kwargs

    def process(self, msg, kwargs):
        """
        Method called to extract the tags from the message
        """
        raw_tags = dict(kwargs)
        raw_tags.update(self._tags)
        tags = "|".join([f"{k}:{v}" for k, v in raw_tags.items()])
        kwargs = {"extra": {"tags": raw_tags}}
        return "[{}] {}".format(tags, msg), kwargs
