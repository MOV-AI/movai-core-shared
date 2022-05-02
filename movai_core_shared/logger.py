"""
   Copyright (C) Mov.ai  - All Rights Reserved
   Unauthorized copying of this file, via any medium is strictly prohibited
   Proprietary and confidential

   Developers:
   - Dor Marcous (dor@mov.ai) - 2022
"""
import logging
import sys
from datetime import datetime
import json
from urllib.parse import urlparse
import http.client
import threading
import requests
from logging.handlers import TimedRotatingFileHandler
from movai_core_shared.envvars import (
    MOVAI_LOGFILE_VERBOSITY_LEVEL,
    MOVAI_HEALTHNODE_VERBOSITY_LEVEL,
    MOVAI_STDOUT_VERBOSITY_LEVEL,
    MOVAI_GENERAL_VERBOSITY_LEVEL,
    LOG_HTTP_HOST,
)

LOG_FORMATTER_DATETIME = "%Y-%m-%d %H:%M:%S"
S_FORMATTER = '[%(levelname)s][%(asctime)s][%(module)s][%(funcName)s][%(tags)s][%(lineno)d]: %(message)s'
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
        if MOVAI_STDOUT_VERBOSITY_LEVEL != logging.NOTSET:
            logger.addHandler(_get_console_handler())
        if MOVAI_LOGFILE_VERBOSITY_LEVEL != logging.NOTSET:
            logger.addHandler(_get_file_handler())
        if MOVAI_HEALTHNODE_VERBOSITY_LEVEL != logging.NOTSET:
            logger.addHandler(_get_healthnode_handler())
        logger.setLevel(MOVAI_GENERAL_VERBOSITY_LEVEL)
        logger.propagate = False
        return logger

    @staticmethod
    def get_logs(limit=1000, offset=0, level=None, tags=None, message=None, from_=None, to_=None, pagination=False,
                 services=None):
        """ Get logs from HealthNode """

        url = f'{LOG_HTTP_HOST}/logs'
        params = {
            'limit': Log.validate_limit(limit),
            'offset': Log.validate_limit(offset),
        }

        if level:
            params['levels'] = Log.validate_level(level)

        if tags:
            params['tags'] = Log.validate_str_list(tags)

        if message:
            params['message'] = Log.validate_message(message)

        if from_:
            params['from'] = int(Log.validate_datetime(from_))

        if to_:
            params['to'] = int(Log.validate_datetime(to_))

        if services is not None:
            params['services'] = services

        try:
            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
        except Exception as e:
            raise e

        try:
            content = response.json()
        except Exception as e:
            logger = Log.get_logger()
            logger.error(message=str(e))
            return []
        else:
            return content if pagination else content.get('data', [])

    @staticmethod
    def validate_limit(value):
        try:
            val = int(value)
        except ValueError:
            raise ValueError('invalid limit/offset value')
        return val

    @staticmethod
    def validate_level(value):
        try:
            if isinstance(value, list):
                values = [x.lower() for x in value]
            elif isinstance(value, str):
                values = [value]
            else:
                raise ValueError("level must be string or list of strings")

            for val in values:
                if val not in ['debug', 'info', 'warning', 'error', 'critical']:
                    raise ValueError(val)

            levels = ','.join(values)
        except ValueError as e:
            raise ValueError(f"invalid level: {str(e)}")
        return levels

    @staticmethod
    def validate_str_list(value):
        try:
            value = [] if value is None else value
            tags = ','.join(value)
        except ValueError:
            raise ValueError('invalid tags value')
        return tags

    @staticmethod
    def validate_message(value):
        return value

    @staticmethod
    def validate_datetime(value):
        """ Validate if value is timestamp or datetime """
        try:
            dt_obj = datetime.fromtimestamp(int(value))
        except (ValueError, TypeError):
            try:
                dt_obj = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
            except Exception:
                raise ValueError('invalid datetime value, expected: <timestamp> | %Y-%m-%d %H:%M:%S')

        return f'{dt_obj.timestamp():.0f}'

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
