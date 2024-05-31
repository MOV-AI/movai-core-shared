from movai_core_shared.logger import Log
import unittest
import mock
import sys


def validate_loglevel(log_level, mock_call):
    return f"[{log_level}]" in mock_call[1][0]


class TestLogging(unittest.TestCase):
    @mock.patch("sys.stderr.write")
    def test_validate_logs(self, stdout):

        log = Log.get_logger("test_logger")

        log.info("im logging info")
        self.assertEqual(len(stdout.mock_calls), 1)
        call = stdout.mock_calls[0]
        self.assertTrue(validate_loglevel("INFO", call))
        self.assertIn("[test_logging][test_validate_logs]", call[1][0])
        self.assertIn("im logging info", call[1][0])

        log.critical("im logging critical")
        self.assertEqual(len(stdout.mock_calls), 2)
        call = stdout.mock_calls[1]
        self.assertTrue(validate_loglevel("CRITICAL", call))
        self.assertIn("[test_logging][test_validate_logs]", call[1][0])
        self.assertIn("im logging critical", call[1][0])

        log.warning("im logging warning")
        self.assertEqual(len(stdout.mock_calls), 3)
        call = stdout.mock_calls[2]
        self.assertTrue(validate_loglevel("WARNING", call))
        self.assertIn("[test_logging][test_validate_logs]", call[1][0])
        self.assertIn("im logging warning", call[1][0])

        log.error("im logging error")
        self.assertEqual(len(stdout.mock_calls), 4)
        call = stdout.mock_calls[3]
        self.assertTrue(validate_loglevel("ERROR", call))
        self.assertIn("[test_logging][test_validate_logs]", call[1][0])
        self.assertIn("im logging error", call[1][0])

    @mock.patch("sys.stdout.write", side_effect=sys.stderr.write)
    def test_log_adapter_logs(self, stdout):
        log = Log.get_callback_logger("test_logger", "test_node", "test_callback")
        log.info("im logging info")

        stdout.assert_called_once()

        call = stdout.mock_calls[0]
        self.assertTrue(validate_loglevel("INFO", call))
        self.assertIn("[test_logging][test_log_adapter_logs]", call[1][0])
        self.assertIn("im logging info", call[1][0])
        self.assertIn("[user_log:True|node:test_node|callback:test_callback]", call[1][0])
