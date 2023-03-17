"""
   Copyright (C) Mov.ai  - All Rights Reserved
   Unauthorized copying of this file, via any medium is strictly prohibited
   Proprietary and confidential

   Developers:
   - Dor Marcous (dor@mov.ai) - 2022
"""
from datetime import datetime
import logging
from logging.handlers import TimedRotatingFileHandler
import threading


from movai_core_shared.consts import (
    LOGS_HANDLER_MSG_TYPE,
    LOGS_QUERY_HANDLER_MSG_TYPE,
    LOGS_MEASUREMENT,
    MAX_LOG_QUERY,
    MIN_LOG_QUERY,
    DEFAULT_LOG_LIMIT,
    DEFAULT_LOG_OFFSET
)
from movai_core_shared.envvars import (
    DEVICE_NAME,
    MOVAI_LOGFILE_VERBOSITY_LEVEL,
    MOVAI_FLEET_LOGS_VERBOSITY_LEVEL,
    MOVAI_STDOUT_VERBOSITY_LEVEL,
    MOVAI_GENERAL_VERBOSITY_LEVEL,
    MESSAGE_SERVER_LOCAL_ADDR,
    MESSAGE_SERVER_REMOTE_ADDR,
    DEVICE_NAME,
    SERVICE_NAME,
)
from movai_core_shared.core.message_client import MessageClient
from movai_core_shared.common.utils import is_enteprise, is_manager
from movai_core_shared.common.time import validate_time

LOG_FORMATTER_DATETIME = "%Y-%m-%d %H:%M:%S"
S_FORMATTER = (
    "[%(levelname)s][%(asctime)s][%(module)s][%(funcName)s][%(tags)s][%(lineno)d]: %(message)s"
)
LOG_FORMATTER = logging.Formatter(
    "[%(levelname)s][%(asctime)s][%(module)s][%(funcName)s][%(lineno)d]: %(message)s",
    datefmt=LOG_FORMATTER_DATETIME,
)


class StdOutHandler(logging.StreamHandler):
    _COLORS = {
        logging.DEBUG: "\x1b[30;1m",  # light black (gray)
        logging.INFO: "",  # default (white)
        logging.WARNING: "\x1b[33;1m",  # yellow
        logging.ERROR: "\x1b[31;1m",  # red
        logging.CRITICAL: "\x1b[41;1m",  # bright red
    }
    _COLOR_RESET = "\u001b[0m"

    def __init__(self, stream=None):
        super().__init__(stream)

    def emit(self, record):
        try:
            # Override the module and funcName with the ones
            if (
                hasattr(record.args, "module")
                and hasattr(record.args, "funcName")
                and hasattr(record.args, "lineno")
            ):
                record.module = record.args.get("module")
                record.funcName = record.args.get("funcName")
                record.lineno = record.args.get("lineno")

            # Add/Remove Tags from log formatter
            _formatter = S_FORMATTER
            if isinstance(record.args, dict) and record.args.get("tags"):
                tags = record.args.get("tags")
                record.tags = "|".join([f"{k}:{v}" for k, v in tags.items()])
            else:
                # if no tags are passed then update formatter
                _formatter = _formatter.replace("[%(tags)s]", "")

            log_format = logging.Formatter(fmt=_formatter, datefmt=LOG_FORMATTER_DATETIME)
            self.setFormatter(fmt=log_format)

            msg = self.format(record)

            stream = self.stream
            stream.write(self._COLORS.get(record.levelno, "") + msg + self._COLOR_RESET)
            stream.write(self.terminator)
            self.flush()
        except Exception:
            self.handleError(record)


class RemoteHandler(logging.StreamHandler):
    """
    This class implemets a log handler which sends
    sends the data to message server for logging in influxdb.
    """

    _measurement = "app_logs"

    def __init__(self):
        """
        Constructor
        """
        logging.StreamHandler.__init__(self, None)
        self._message_client = MessageClient(MESSAGE_SERVER_LOCAL_ADDR)

    def emit(self, record):
        """
        Emit a record.
        Send the record to the HealthNode API

        Args:
            record: The python log message data record

        """
        threading.Thread(target=self._emit, args=(record,)).start()

    def _emit(self, record):
        """
        Builds a valid log message request from the python log record
        and send it to the local message server

        Args:
            record: The Python log message data record

        """
        log_tags = {"robot": DEVICE_NAME, "level": record.levelname, "service": SERVICE_NAME}

        if hasattr(record, "tags"):
            log_tags.update(record.tags)

        log_fields = {
            "module": record.module,
            "funcName": record.funcName,
            "lineno": record.lineno,
            "message": record.msg,
        }

        log_data = {
            "measurement": self._measurement,
            "log_tags": log_tags,
            "log_fields": log_fields,
        }

        self._message_client.send_request(LOGS_HANDLER_MSG_TYPE, log_data)


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


def get_remote_handler(log_level=logging.NOTSET):
    """
    Create a RemoteHandler object and return it

    Args:
        log_level: defines the remote logger log level default value is info

    Returns: ReomoteLogger object

    """
    remote_handler = RemoteHandler()
    if log_level in [
        logging.CRITICAL,
        logging.FATAL,
        logging.ERROR,
        logging.WARNING,
        logging.INFO,
        logging.DEBUG,
    ]:
        remote_handler.setLevel(log_level)
    else:
        remote_handler.setLevel(MOVAI_FLEET_LOGS_VERBOSITY_LEVEL)

    return remote_handler


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
        if is_enteprise():
            if MOVAI_FLEET_LOGS_VERBOSITY_LEVEL != logging.NOTSET:
                logger.addHandler(get_remote_handler())
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


class LogsQuery:
    """A class for querying logs"""

    _min_val = MIN_LOG_QUERY
    _max_val = MAX_LOG_QUERY

    @classmethod
    def validate_value(cls, filter_name: str, value: int) -> int:
        """Validates the limmit.

        Args:
            filter_name (str): Which filter called the validation function.
            value (int): The limit to validate.
            alternate_value (int): an alternative value in case of error.

        Raises:
            ValueError: in case limit can not be casted to int.

        Returns:
            int: The validated limit.
        """
        try:
            val = int(value)
        except ValueError:
            raise ValueError(f"{value} is Invalid {filter_name} value")

        if val < cls._min_val:
            raise ValueError(f"{filter_name} value: {value} must be greater than {cls._min_val}")
        elif val > cls._max_val:
            raise ValueError(f"{filter_name} value: {value} must be lower than {cls._max_val}")

        return val

    @classmethod
    def validate_message(cls, value: str) -> str:
        """Validates the message

        Args:
            value (str): A message to validate

        Raises:
            ValueError: In case message is not a string.

        Returns:
            str: The message.
        """
        if not isinstance(value, str):
            raise ValueError("Invalid message, message must be a string.")
        return value

    @classmethod
    def validate_datetime(cls, value: int) -> str:
        """Validate if value is timestamp or datetime

        Args:
            value (int): The datetime to validate

        Raises:
            ValueError: In case value isn't a time format.

        Returns:
            int: a timestamp value.
        """
        try:
            dt_obj = datetime.fromtimestamp(int(value))
        except (ValueError, TypeError):
            try:
                dt_obj = datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
            except Exception:
                raise ValueError(
                    "invalid datetime value, expected: <timestamp> | %Y-%m-%d %H:%M:%S"
                )

        return int(dt_obj.timestamp())

    @classmethod
    def get_logs(
        cls,
        limit=DEFAULT_LOG_LIMIT,
        offset=DEFAULT_LOG_OFFSET,
        robots=None,
        services=None,
        level=None,
        message=None,
        fromDate=None,
        toDate=None,
        pagination=False,
        **kwrargs
    ):
        """Get logs from message-server"""
        server_addr = MESSAGE_SERVER_REMOTE_ADDR
        if is_manager():
            server_addr = MESSAGE_SERVER_LOCAL_ADDR

        message_client = MessageClient(server_addr)
        params = {}

        if limit is not None:
            params["limit"] = cls.validate_value("limit", limit)

        if offset is not None:
            params["offset"] = cls.validate_value("offset", offset)

        if robots is not None:
            params["robot"] = robots

        if level is not None:
            params["level"] = level

        if message is not None:
            params["message"] = cls.validate_message(message)

        if fromDate is not None:
            params["fromDate"] = validate_time(fromDate)

        if toDate is not None:
            params["toDate"] = validate_time(toDate)

        if services is not None:
            params["service"] = services

        if kwrargs:
            if "tags" in kwrargs:
                params["tag"] = kwrargs["tags"]
            else:
                params["tag"] = kwrargs

        query_data = {
            "measurement": LOGS_MEASUREMENT,
            "query_data": params,
            "count_field": "message",
        }

        try:
            query_response = message_client.send_request(
                LOGS_QUERY_HANDLER_MSG_TYPE, query_data, None, True
            )
            response = query_response["data"]
        except Exception as error:
            raise error

        return response if pagination else response.get("data", [])
