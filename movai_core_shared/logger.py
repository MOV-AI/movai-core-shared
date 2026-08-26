"""Copyright (C) Mov.ai  - All Rights Reserved
Unauthorized copying of this file, via any medium is strictly prohibited
Proprietary and confidential

Developers:
- Dor Marcous (dor@mov.ai) - 2022

"""
import sys
import logging
import syslog

from movai_core_shared.consts import (
    LOG_TEXT_FORMAT,
    LOG_DATE_FORMAT,
    LOG_FORMATTER,
    USER_LOG_TAG,
    CALLBACK_LOGGER,
    CALLBACK_STDOUT_COLORS,
    SPAWNER_STDOUT_COLORS,
)
from movai_core_shared.envvars import (
    MOVAI_LOG_FILE,
    MOVAI_STDOUT_VERBOSITY_LEVEL,
    MOVAI_GENERAL_VERBOSITY_LEVEL,
    MOVAI_CALLBACK_VERBOSITY_LEVEL,
    DETACHED_PROCESS_OUTPUT,
)
from movai_core_shared.log_handlers.callback_handler import (
    CallbackStdOutHandler,
    CallbackLogAdapter,
)
from movai_core_shared.log_handlers.generic_handler import LogAdapter


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
