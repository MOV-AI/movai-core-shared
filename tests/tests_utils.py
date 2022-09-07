"""
   Copyright (C) Mov.ai  - All Rights Reserved
   Unauthorized copying of this file, via any medium is strictly prohibited
   Proprietary and confidential

   Developers:
   - Ofer Katz (ofer@mov.ai) - 2022

   Utility class for reading the message client messages and
   validations for the client message handler tests
"""

import os
import json
import zmq
from movai_core_shared.envvars import MSG_HANDLER_LOCAL_CONN

os.environ['DEVICE_NAME'] = 'developbot'
os.environ['SERVICE'] = 'node_runner'
os.environ['DEVICE_ID'] = '242171c4ae824c7f92a54cac60604d85'

expected_tags = {
    'fleet': 'movai',
    'robot_id': '242171c4ae824c7f92a54cac60604d85',
    'robot': 'developbot',
    'service': 'node_runner'
}


class TestsUtils:
    _socket = zmq.Context().socket(zmq.DEALER)

    @staticmethod
    def bind_to_test_client():
        TestsUtils._socket.setsockopt(zmq.RCVTIMEO, 200)
        # Connect to the local message server
        TestsUtils._socket.bind(MSG_HANDLER_LOCAL_CONN)

    @staticmethod
    def get_msg():
        try:
            resp_buff = TestsUtils._socket.recv()
            response = json.loads(resp_buff)
            response['status'] = 'OK'
        except zmq.Again:
            response = {'status': 'ERROR - Receive Timeout'}

        return response

    @staticmethod
    def validate_response(response: dict, expected_result: dict) -> bool:
        ret_val = True
        for key in expected_result:
            if key not in response or response[key] != expected_result[key]:
                ret_val = False
                break

        return ret_val

    @staticmethod
    def validate_tags(tags: dict) -> bool:
        ret_val = True
        for key in expected_tags:
            if key not in tags or tags[key] != expected_tags[key]:
                ret_val = False
                break

        return ret_val
