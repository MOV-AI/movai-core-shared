"""
   Copyright (C) Mov.ai  - All Rights Reserved
   Unauthorized copying of this file, via any medium is strictly prohibited
   Proprietary and confidential

   Developers:
   - Duarte Coelho (duarte@mov.ai) - 2025
   - David Dias (david.dias@mov.ai) - 2025
   - Andre Pereira (andre.pereira@mov.ai) - 2025
"""

import sys
import logging
from movai_core_shared.log_handlers.generic_handler import LogAdapter
from movai_core_shared.consts import (
    CALLBACK_STDOUT_COLORS,
)

LOG_FORMATTER_DATETIME = "%Y-%m-%d %H:%M:%S"
CALLBACK_LOG_FORMAT = (
    "[%(levelname)s][%(asctime)s][%(node)s][%(callback)s][%(lineno)d]: %(message)s"
)


class CallbackStdOutHandler(logging.StreamHandler):
    _COLORS = CALLBACK_STDOUT_COLORS
    _COLOR_RESET = "\u001b[0m"

    def __init__(self, color=CALLBACK_STDOUT_COLORS, stream=None):
        super().__init__(stream)
        self._COLORS = color
        self.setFormatter(
            logging.Formatter(fmt=CALLBACK_LOG_FORMAT, datefmt=LOG_FORMATTER_DATETIME)
        )

    def emit(self, record):
        try:
            # Override the module and funcName with the ones

            if (
                isinstance(record.args, dict)
                and "module" in record.args
                and "funcName" in record.args
                and "lineno" in record.args
            ):
                record.module = record.args.get("module")
                record.funcName = record.args.get("funcName")
                record.lineno = record.args.get("lineno")

            # Add/Remove Tags from log formatter
            if isinstance(record.args, dict) and record.args.get("tags"):
                tags = record.args.get("tags")
                record.tags = "|".join([f"{k}:{v}" for k, v in tags.items()])

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
            self.handleError(record)


class CallbackLogAdapter(LogAdapter):
    """
    A LogAdapter used to expose the logger inside a callback.

    py_logger = Log.get_logger("logger name")
    logger = LogAdapter(py_logger, tag1="value", tag2="value")

    Usage:
        logger.debug(<message>, <tagKey>=<tagValue>, <tagKey>=<tagValue>...)
        logger.info(<message>, <tagKey>=<tagValue>, <tagKey>=<tagValue>...)
        logger.warning(<message>, <tagKey>=<tagValue>, <tagKey>=<tagValue>...)
        logger.error(<message>, <tagKey>=<tagValue>, <tagKey>=<tagValue>...)
        logger.critical(<message>, <tagKey>=<tagValue>, <tagKey>=<tagValue>...)

    """

    def __init__(self, logger, callback_name=None, node_name=None, **kwargs):
        super().__init__(logger, **kwargs)
        self._tags = kwargs
        self.node_name = node_name
        self.callback_name = callback_name

    def process(self, msg, kwargs):
        """
        Method called to extract the tags from the message
        """
        raw_tags = dict(kwargs)
        raw_tags.update(self._tags)
        if raw_tags:
            tags = "|".join([f"{k}:{v}" for k, v in raw_tags.items()])

        kwargs = {
            "extra": {"tags": raw_tags, "callback": self.callback_name, "node": self.node_name}
        }

        if raw_tags:
            return f"[{tags}] {msg}", kwargs

        return f"{msg}", kwargs
