import logging
from movai_core_shared.logger import Log, LogAdapter
from movai_core_shared.exceptions import MovaiException


def check_log(caplog, expected):
    """help function to validate the log"""
    assert caplog.text == expected
    caplog.clear()


def check_trackback(caplog, should_have_trackback):
    """help function to validate the log"""
    if should_have_trackback:
        assert "Traceback" in caplog.text
    else:
        assert "Traceback" not in caplog.text
    caplog.clear()


def test_logger(caplog):
    """Test for the logger that will generate new logger with get_logger
    and test out all the different verbosity and check the logs that are correct
    """
    caplog.set_level(logging.DEBUG, logger="test_logger")
    log = Log.get_logger("test_logger")
    log.addHandler(caplog.handler)
    logger = LogAdapter(log)
    try:
        log.info("in try log")
        check_log(caplog, "INFO     test_logger:test_logger.py:30 in try log\n")
        logger.error("in try logger")
        check_log(caplog, "ERROR    test_logger:test_logger.py:32 [user_log:True] in try logger\n")
        log.debug("a %s 2 %f 3 %i" % ("a", 2, 3))
        check_log(caplog, "DEBUG    test_logger:test_logger.py:34 a a 2 2.000000 3 3\n")
        msg = "message"
        logger.warning(f"this is a {msg}")
        check_log(caplog, "WARNING  test_logger:test_logger.py:37 [user_log:True] this is a message\n")
        raise MovaiException("test error")
    except MovaiException as e:
        logger.error("test error logger", e)
        check_trackback(caplog, True)
        logger.warning(f"test error 2 logger e:{e}")
        check_trackback(caplog, False)
        log.error(f"test log error e:{e}")
        check_trackback(caplog, False)
        logger.info("test logger info e:{e}")
        check_trackback(caplog, False)
        logger.critical("last")
        check_trackback(caplog, True)
    assert True
