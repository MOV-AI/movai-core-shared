import logging
from movai_core_shared.logger import Log, LogAdapter
from movai_core_shared.exceptions import MovaiException
import os
import re
import mock


def check_log(caplog, expected):
    """help function to validate the log"""
    # Replace the log line number with an X
    expected_pattern = re.sub(r'test_logger.py:\d+', 'test_logger.py:X', expected)
    text_pattern = re.sub(r'test_logger.py:\d+', 'test_logger.py:X', caplog.text)
    assert text_pattern == expected_pattern
    caplog.clear()


def check_trackback(caplog, should_have_trackback):
    """help function to validate the log"""
    if should_have_trackback:
        assert "Traceback" in caplog.text
    else:
        assert "Traceback" not in caplog.text
    caplog.clear()


# def test_logger(caplog):
#     """Test for the logger that will generate new logger with get_logger
#     and test out all the different verbosity and check the logs that are correct
#     """
#     caplog.set_level(logging.DEBUG, logger="test_logger")
#     log = Log.get_logger("test_logger")
#     log.addHandler(caplog.handler)
#     logger = LogAdapter(log)
#     try:
#         # Info log
#         log.info("in try log info")
#         check_log(caplog, "INFO     test_logger:test_logger.py:36 in try log info\n")
#         logger.info("in try logAdapter info")
#         check_log(caplog, "INFO     test_logger:test_logger.py:36 [] in try logAdapter info\n")
#         # Error log
#         logger.error("in try logger error")
#         check_log(caplog, "ERROR    test_logger:test_logger.py:38 [] in try logger error\n")
#         logger.error("in try logAdapter error")
#         check_log(caplog, "ERROR    test_logger:test_logger.py:38 [] in try logAdapter error\n")
#         # Warning log
#         msg = "message"
#         log.warning(f"log this is a {msg}")
#         check_log(caplog, "WARNING  test_logger:test_logger.py:43 log this is a message\n")
#         logger.warning(f"logAdapter this is a {msg}")
#         check_log(caplog, "WARNING  test_logger:test_logger.py:43 [] logAdapter this is a message\n")
#         # Debug log
#         log.debug("in try log info")
#         check_log(caplog, "")
#         logger.debug("in try logAdapter info")
#         check_log(caplog, "")
#         # Test formats
#         log.info("a %s 2 %f 3 %i" % ("a", 2, 3))
#         check_log(caplog, "INFO     test_logger:test_logger.py:40 a a 2 2.000000 3 3\n")
#         raise MovaiException("test error")
#     except MovaiException as e:
#         logger.error("test error logger", e)
#         check_trackback(caplog, True)
#         logger.warning(f"test error 2 logger e:{e}")
#         check_trackback(caplog, False)
#         log.error(f"test log error e:{e}")
#         check_trackback(caplog, False)
#         logger.info("test logger info e:{e}")
#         check_trackback(caplog, False)
#         logger.critical("last")
#         check_trackback(caplog, True)

#     assert True
