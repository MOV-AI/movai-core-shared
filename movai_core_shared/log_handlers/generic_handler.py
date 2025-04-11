import logging
import sys
import traceback

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

    def _exc_tb(self):
        """get latest exception (if any) and format it
        only works "inside" an `except` block"""
        etype, exc, tb = sys.exc_info()
        if exc is None:
            # no exception
            return ""
        return "\n" + str.join("", traceback.format_exception(etype, exc, tb)).strip().replace(
            "%", "%%"
        )  # final new line

    def get_message(self, *args, **kwargs):
        if "message" in kwargs:
            message = kwargs.get("message", "")
        elif "msg" in kwargs:
            message = kwargs.get("msg", "")
        else:
            message = str(args[0])
        message, kwargs = self.process(message, kwargs)
        message += self._exc_tb()
        return message, kwargs

    def error(self, *args, **kwargs):
        new_msg, kwargs = self.get_message(*args, **kwargs)
        self.logger.error(new_msg, stacklevel=3, **kwargs)

    def critical(self, *args, **kwargs):
        new_msg, kwargs = self.get_message(*args, **kwargs)
        self.logger.critical(new_msg, stacklevel=3, **kwargs)

    def process(self, msg, kwargs):
        """
        Method called to extract the tags from the message
        """
        raw_tags = dict(kwargs)
        raw_tags.update(self._tags)
        tags = "|".join([f"{k}:{v}" for k, v in raw_tags.items()])
        kwargs = {"extra": {"tags": raw_tags}}

        return f"[{tags}] {msg}", kwargs