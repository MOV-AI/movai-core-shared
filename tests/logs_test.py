
"""
   Copyright (C) Mov.ai  - All Rights Reserved
   Unauthorized copying of this file, via any medium is strictly prohibited
   Proprietary and confidential

   Developers:
   - Ofer Katz (ofer@mov.ai) - 2022

   logs tests suite
"""

import logging
import unittest
from movai_core_shared.logger import Log
from .tests_utils import TestsUtils

expected_res = {
    'level': 'INFO',
    'message': '1234, one, two three!!!',
    'module': 'logs_test',
}


class LogsTestSuite(unittest.TestCase):
    @staticmethod
    def test_send_info_log_message_log_level_set_to_info():
        res = False
        TestsUtils.bind_to_test_client()
        logger = Log.get_logger('remote_logger_tester')
        Log.set_remote_logger_level(logger, logging.INFO)
        logger.info('1234, one, two three!!!')
        response = TestsUtils.get_msg()
        if response['status'] == 'OK':
            log_data = response.get('request').get('req_data').get('fields')
            response_tags = response.get('request').get('req_data').get('tags')
            expected_res['funcName'] = 'test_send_info_log_message_log_level_set_to_info'
            if log_data is not None:
                res = TestsUtils.validate_response(log_data, expected_res)
                if res and response_tags is not None:
                    res = TestsUtils.validate_tags(response_tags)
                else:
                    res = False

        assert res

    @staticmethod
    def test_send_info_log_message_log_level_set_to_error():
        TestsUtils.bind_to_test_client()
        logger = Log.get_logger('remote_logger_tester')
        Log.set_remote_logger_level(logger, logging.ERROR)
        logger.info('1234, one, two three!!!')
        response = TestsUtils.get_msg()
        if response['status'] == 'OK':
            assert False

        assert True

    @staticmethod
    def test_send_info_log_message_log_level_set_to_debug():
        res = False
        TestsUtils.bind_to_test_client()
        logger = Log.get_logger('remote_logger_tester')
        Log.set_remote_logger_level(logger, logging.DEBUG)
        logger.info('1234, one, two three!!!')
        response = TestsUtils.get_msg()
        if response['status'] == 'OK':
            log_data = response.get('request').get('req_data').get('fields')
            response_tags = response.get('request').get('req_data').get('tags')
            expected_res['funcName'] = 'test_send_info_log_message_log_level_set_to_debug'
            if log_data is not None:
                res = TestsUtils.validate_response(log_data, expected_res)
                if res and response_tags is not None:
                    res = TestsUtils.validate_tags(response_tags)
                else:
                    res = False

        assert res
