"""Copyright (C) Mov.ai  - All Rights Reserved
Unauthorized copying of this file, via any medium is strictly prohibited
Proprietary and confidential

Developers:
- Dor Marcous (dor@mov.ai) - 2022

"""
import asyncio
import sys
import logging
from logging.handlers import TimedRotatingFileHandler
import syslog
import json

from movai_core_shared import __version__ as VERSION
from movai_core_shared.common.time import current_timestamp_int

from movai_core_shared.consts import (
    DEFAULT_LOG_LIMIT,
    DEFAULT_LOG_OFFSET,
    LOG_TEXT_FORMAT,
    LOG_DATE_FORMAT,
    LOG_FORMATTER,
    LOGS_HANDLER_MSG_TYPE,
    LOGS_QUERY_HANDLER_MSG_TYPE,
    LOGS_MEASUREMENT,
    SYSLOG_MEASUREMENT,
    SYSLOGS_HANDLER_MSG_TYPE,
    PID,
    USER_LOG_TAG,
    CALLBACK_LOGGER,
    CALLBACK_STDOUT_COLORS,
    SPAWNER_STDOUT_COLORS,
)
from movai_core_shared.envvars import (
    DEVICE_NAME,
    MOVAI_LOGFILE_VERBOSITY_LEVEL,
    MOVAI_LOG_FILE,
    MOVAI_FLEET_LOGS_VERBOSITY_LEVEL,
    MOVAI_STDOUT_VERBOSITY_LEVEL,
    MOVAI_GENERAL_VERBOSITY_LEVEL,
    MOVAI_CALLBACK_VERBOSITY_LEVEL,
    LOCAL_MESSAGE_SERVER,
    MASTER_MESSAGE_SERVER,
    SERVICE_NAME,
    SYSLOG_ENABLED,
    DETACHED_PROCESS_OUTPUT,
)
from movai_core_shared.messages.metric_data import LogQueryResponse
from movai_core_shared.core.message_client import MessageClient, AsyncMessageClient
from movai_core_shared.common.utils import is_enterprise, is_manager
from movai_core_shared.common.time import validate_time
from movai_core_shared.log_handlers.callback_handler import (
    CallbackStdOutHandler,
    CallbackLogAdapter,
)
from movai_core_shared.log_handlers.generic_handler import LogAdapter
from .base_query import BaseQuery


# pylint: disable=invalid-name,dangerous-default-value,protected-access,no-member,no-else-raise,too-many-arguments,too-many-locals,too-many-branches

S_FORMATTER = (
    "[%(levelname)s][%(asctime)s][%(module)s][%(funcName)s][%(tags)s][%(lineno)d]: %(message)s"
)

SEVERETY_CODES_MAPPING = {
    "CRITICAL": syslog.LOG_CRIT,
    "ERROR": syslog.LOG_ERR,
    "WARNING": syslog.LOG_WARNING,
    "INFO": syslog.LOG_INFO,
    "DEBUG": syslog.LOG_DEBUG,
}

logging.getLogger("rosout").setLevel(MOVAI_CALLBACK_VERBOSITY_LEVEL)


class StdOutHandler(logging.StreamHandler):
    _COLORS = SPAWNER_STDOUT_COLORS
    _COLOR_RESET = "\u001b[0m"

    def __init__(self, color=SPAWNER_STDOUT_COLORS, stream=None):
        super().__init__(stream)
        self._COLORS = color

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
                _formatter = _formatter.replace("[%(tags)s]", "")
            log_format = logging.Formatter(fmt=_formatter, datefmt=LOG_DATE_FORMAT)
            self.setFormatter(fmt=log_format)

            msg = self.format(record)
            stream = self.stream
            if stream.closed:
                if stream == sys.stderr:
                    stream = open("/dev/stderr", "w")
                else:
                    stream = open("/dev/stdout", "w")
            stream.write(
                self._COLORS.get(record.levelno, "") + msg + self._COLOR_RESET + self.terminator
            )
            # stream.write()
            self.flush()
        except Exception:
            logger = logging.getLogger(__name__)
            logger.exception("An error occurred while emitting a log record.")


logging.getLogger("rosout").addHandler(
    StdOutHandler(color=CALLBACK_STDOUT_COLORS, stream=sys.stdout)
)
logging.getLogger("rosout").propagate = False


class RemoteHandler(logging.StreamHandler):
    """
    This class implemets a log handler which sends
    sends the data to message server for logging in influxdb.
    """

    def __init__(self):
        """
        Constructor
        """
        logging.StreamHandler.__init__(self, None)
        self._message_client = MessageClient(LOCAL_MESSAGE_SERVER)
        self._async_message_client = AsyncMessageClient(LOCAL_MESSAGE_SERVER)

    def emit(self, record):
        """
        Builds a valid log message request from the python log record
        and send it to the local message server

        Args:
            record: The Python log message data record

        """
        if isinstance(record.msg, Exception):
            record.msg = str(record.msg)

        log_tags = {"robot": DEVICE_NAME, "level": record.levelname, "service": SERVICE_NAME}

        syslog_tags = {
            "appname": SERVICE_NAME,
            "facility": "console",
            "host": DEVICE_NAME,
            "hostname": DEVICE_NAME,
            "severity": record.levelname,
        }

        if hasattr(record, "tags"):
            log_tags.update(record.tags)
            syslog_tags.update(record.tags)

        log_fields = {
            "module": record.module,
            "funcName": record.funcName,
            "lineno": record.lineno,
            "message": record.msg,
        }
        if record.args:
            # if not serializable, convert to string
            log_fields["args"] = json.dumps(record.args, default=str)

        syslog_fields = {
            "module": record.module,
            "funcName": record.funcName,
            "lineno": record.lineno,
            "facility_code": 14,
            "message": record.msg,
            "procid": PID,
            "severity_code": SEVERETY_CODES_MAPPING[record.levelname],
            "timestamp": current_timestamp_int(),
            "version": VERSION,
        }

        log_data = {
            "measurement": LOGS_MEASUREMENT,
            "log_tags": log_tags,
            "log_fields": log_fields,
        }

        syslog_data = {
            "measurement": SYSLOG_MEASUREMENT,
            "log_tags": syslog_tags,
            "log_fields": syslog_fields,
        }

        if asyncio._get_running_loop() is not None:
            asyncio.create_task(
                self._async_message_client.send_request(LOGS_HANDLER_MSG_TYPE, log_data)
            )
            if SYSLOG_ENABLED:
                asyncio.create_task(
                    self._async_message_client.send_request(SYSLOGS_HANDLER_MSG_TYPE, syslog_data)
                )
            return

        self._message_client.send_request(LOGS_HANDLER_MSG_TYPE, log_data)
        if SYSLOG_ENABLED:
            self._message_client.send_request(SYSLOGS_HANDLER_MSG_TYPE, syslog_data)


def _get_console_handler(stream_config=None):
    """
    Set up the stdout handler
    """
    if stream_config is None:
        console_handler = StdOutHandler()
        console_handler.setFormatter(LOG_FORMATTER)
    elif stream_config == CALLBACK_LOGGER:
        console_handler = CallbackStdOutHandler(stream=sys.stdout)
    else:
        raise ValueError("Unknown stream config for the console logger!")
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


def add_shared_handler_to_root():
    """Add handler to root so logs can be tailed and redirected to e.g. docker logs."""
    handler = logging.FileHandler(DETACHED_PROCESS_OUTPUT)
    handler.setFormatter(logging.Formatter(LOG_TEXT_FORMAT))
    root = logging.getLogger()
    root.addHandler(handler)
    root.setLevel(logging.DEBUG)


class Log:
    """
    A static class to help create logger instances
    """

    LOG_FILE = MOVAI_LOG_FILE

    @staticmethod
    def set_log_file(name: str):
        """
        Set the name of the file we write the log
        """
        Log.LOG_FILE = name

    @staticmethod
    def get_logger(logger_name: str, stream_config=None):
        """
        Get a logger instance
        """
        logger = logging.getLogger(logger_name)
        if logger.hasHandlers():
            logger.handlers = []
        if MOVAI_STDOUT_VERBOSITY_LEVEL != logging.NOTSET:
            logger.addHandler(_get_console_handler(stream_config))
        if MOVAI_LOGFILE_VERBOSITY_LEVEL != logging.NOTSET:
            logger.addHandler(_get_file_handler())
        if is_enterprise() and MOVAI_FLEET_LOGS_VERBOSITY_LEVEL != logging.NOTSET:
            logger.addHandler(get_remote_handler())
        logger.setLevel(MOVAI_GENERAL_VERBOSITY_LEVEL)
        return logger

    @classmethod
    def get_user_logger(cls, logger_name: str, **tags: dict) -> LogAdapter:
        """Add 'user_log=True' tag to the logger.

        Args:
            logger_name (str): The name of the logger.

        Returns:
            LogAdapter: A logger with tags.
        """
        tags[USER_LOG_TAG] = True
        user_logger = LogAdapter(cls.get_logger(logger_name), **tags)

        return user_logger

    @classmethod
    def get_callback_logger(
        cls, logger_name: str, node_name: str, callback_name: str
    ) -> LogAdapter:
        """Gets the callback the logger.

        Args:
            logger_name (str): The name of the logger.

        Returns:
            LogAdapter: A logger with tags.
        """
        tags = {}
        _logger = cls.get_logger(logger_name, CALLBACK_LOGGER)
        _logger.setLevel(MOVAI_CALLBACK_VERBOSITY_LEVEL)
        logger = CallbackLogAdapter(
            _logger, **tags, node_name=node_name, callback_name=callback_name
        )
        return logger


class LogsQuery(BaseQuery):
    """A class for querying logs"""

    @classmethod
    async def get_logs(
        cls,
        limit=DEFAULT_LOG_LIMIT,
        offset=DEFAULT_LOG_OFFSET,
        robots=None,
        services=None,
        level=None,
        message=None,
        fromDate=None,
        toDate=None,
        order_by=None,
        order_dir=None,
        **kwrargs,
    ) -> LogQueryResponse:
        """Get logs from message-server"""
        server_addr = MASTER_MESSAGE_SERVER
        if is_manager():
            server_addr = LOCAL_MESSAGE_SERVER

        message_client = AsyncMessageClient(server_addr)
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

        if order_by is not None:
            params["order_by"] = order_by

        if order_dir is not None:
            params["order_dir"] = order_dir

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

        query_response = await message_client.send_request(
            LOGS_QUERY_HANDLER_MSG_TYPE, query_data, None, True
        )

        return LogQueryResponse(**(query_response["response"]))
