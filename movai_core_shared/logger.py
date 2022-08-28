"""
   Copyright (C) Mov.ai  - All Rights Reserved
   Unauthorized copying of this file, via any medium is strictly prohibited
   Proprietary and confidential

   Developers:
   - Dor Marcous (dor@mov.ai) - 2022
"""
import logging
from datetime import datetime
import requests
from logging.handlers import TimedRotatingFileHandler
from movai_core_shared.envvars import (
    MOVAI_LOGFILE_VERBOSITY_LEVEL,
    MOVAI_FLEET_LOGS_VERBOSITY_LEVEL,
    MOVAI_STDOUT_VERBOSITY_LEVEL,
    MOVAI_GENERAL_VERBOSITY_LEVEL
)
try:
    from movai_core_enterprise.message_client_handlers.remote_logger import get_remote_logger_client
    enterprise = True
except ImportError:
    enterprise = False

LOG_FORMATTER_DATETIME = "%Y-%m-%d %H:%M:%S"
S_FORMATTER = '[%(levelname)s][%(asctime)s][%(module)s][%(funcName)s][%(tags)s][%(lineno)d]: %(message)s'
LOG_FORMATTER = logging.Formatter(
    "[%(levelname)s][%(asctime)s][%(module)s][%(funcName)s][%(lineno)d]: %(message)s",
    datefmt=LOG_FORMATTER_DATETIME,
)


class StdOutHandler(logging.StreamHandler):
    _COLORS = {
        logging.DEBUG: '\x1b[30;1m',  # light black (gray)
        logging.INFO: '',  # default (white)
        logging.WARNING: '\x1b[33;1m',  # yellow
        logging.ERROR: '\x1b[31;1m',  # red
        logging.CRITICAL: '\x1b[41;1m'  # bright red
    }
    _COLOR_RESET = '\u001b[0m'

    def __init__(self, stream=None):
        super().__init__(stream)

    def emit(self, record):
        try:
            # Override the module and funcName with the ones
            if hasattr(record.args,'module') and hasattr(record.args,'funcName') and hasattr(record.args,'lineno'):
                record.module = record.args.get('module')
                record.funcName = record.args.get('funcName')
                record.lineno = record.args.get('lineno')

            # Add/Remove Tags from log formatter
            _formatter = S_FORMATTER
            if isinstance(record.args, dict) and record.args.get('tags'):
                tags = record.args.get('tags')
                record.tags = '|'.join([f'{k}:{v}' for k, v in tags.items()])
            else:
                # if no tags are passed then update formatter
                _formatter = _formatter.replace('[%(tags)s]', '')

            log_format = logging.Formatter(
                fmt=_formatter,
                datefmt=LOG_FORMATTER_DATETIME
            )
            self.setFormatter(fmt=log_format)

            msg = self.format(record)

            stream = self.stream
            stream.write(
                self._COLORS.get(record.levelno, '') + msg + self._COLOR_RESET)
            stream.write(self.terminator)
            self.flush()
        except Exception:
            self.handleError(record)


def _get_console_handler():
    """
    Set up the stdout handler
    """
    console_handler = StdOutHandler()
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
        if logger.hasHandlers():
            logger.handlers = []
        if MOVAI_STDOUT_VERBOSITY_LEVEL != logging.NOTSET:
            logger.addHandler(_get_console_handler())
        if MOVAI_LOGFILE_VERBOSITY_LEVEL != logging.NOTSET:
            logger.addHandler(_get_file_handler())
        if enterprise:
            if MOVAI_FLEET_LOGS_VERBOSITY_LEVEL != logging.NOTSET:
                logger.addHandler(get_remote_logger_client())
        logger.setLevel(MOVAI_GENERAL_VERBOSITY_LEVEL)
        logger.propagate = False
        return logger

    @staticmethod
    def _find_between(s, start, end):
        return (s.split(start))[1].split(end)[0]

    @staticmethod
    def _filter_data(*args, **kwargs):
        # Get message stf from args or kwargs
        try:
            message = str(args[0]) % args[1:] if args else str(kwargs.get('message', '')) % args

        except TypeError as e:
            message = " ".join(args)

        # Search and remove fields
        fields = {**kwargs}
        for k, v in fields.items():
            if k in ['message', 'level', 'frame_info']:
                del (kwargs[k])
        return message


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
        return f"[{tags}] {msg}", kwargs
