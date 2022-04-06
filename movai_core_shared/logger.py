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
from movai_core_shared.envvars import (
    MOVAI_LOGFILE_VERBOSITY_LEVEL,
    MOVAI_HEALTHNODE_VERBOSITY_LEVEL,
    MOVAI_STDOUT_VERBOSITY_LEVEL,
    MOVAI_GENERAL_VERBOSITY_LEVEL,
    LOG_HTTP_HOST,
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


class HealthNodeHandler(logging.handlers.HTTPHandler):

    def __init__(self, url):
        logging.Handler.__init__(self)

        parsed_uri = urlparse(url)

        self.host = parsed_uri.netloc
        self.port = None

        try:
            self.host, self.port = self.host.split(':')
        except ValueError:
            # simply host, no port
            pass

        self.url = parsed_uri.path
        self.method = 'POST'
        self.secure = False
        self.credentials = False

    def emit(self, record):
        """
        Emit a record.
        Send the record to the HealthNode API
        """
        threading.Thread(target=self._emit, args=(record,)).start()

    def _emit(self, record):

        try:
            conn = http.client.HTTPConnection(self.host, port=self.port)

            # Log data

            data = self.mapLogRecord(record)
            data = json.dumps(data)

            headers = {
                'Content-type': 'application/json',
                'Content-length': str(len(data))
            }

            conn.request(self.method, self.url, data, headers)
            conn.getresponse()  # can't do anything with the result

        except Exception as e:
            self.handleError(record)


def _get_healthnode_handler():
    _host_http_log_handler = f'{LOG_HTTP_HOST}/logs'
    healthnode_handler = HealthNodeHandler(url=_host_http_log_handler)
    healthnode_handler.setLevel(MOVAI_HEALTHNODE_VERBOSITY_LEVEL)
    return healthnode_handler


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
        if MOVAI_HEALTHNODE_VERBOSITY_LEVEL != logging.NOTSET:
            logger.addHandler(_get_healthnode_handler())
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
        return f"[{tags}] {msg}", kwargs
