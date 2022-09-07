"""
   Copyright (C) Mov.ai  - All Rights Reserved
   Unauthorized copying of this file, via any medium is strictly prohibited
   Proprietary and confidential

   Usage:
        Base class for all remote message handler.
        Sends messages to the robot Message-Server component

   Developers:
   - Ofer Kazt (ofer@mov.ai) - 2022
"""
import json
import os
import random
import logging
import zmq
from movai_core_shared.envvars import (MOVAI_ZMQ_RECV_TIMEOUT_MS, MSG_HANDLER_LOCAL_CONN)


class MessageClient:
    def __init__(self, msg_type, measurement):
        """
        constructor

        Args:
            msg_type: The handler name for handling the message
            measurement: The time-series DB name for storing the data

        """
        self._get_robot_info()

        self._msg_type = msg_type
        self._measurement = measurement

        # ZMQ settings:
        random.seed() # setting the seed for the random number generator
        identity = f"{msg_type}_message_client_{random.getrandbits(24)}".encode('utf8')
        zmq_ctx = zmq.Context()
        # creating the ZMQ socket for sending the request
        self._socket = zmq_ctx.socket(zmq.DEALER)
        self._socket.setsockopt(zmq.IDENTITY, identity)
        self._socket.setsockopt(zmq.RCVTIMEO, int(MOVAI_ZMQ_RECV_TIMEOUT_MS))
        # Connect to the local message server
        self._socket.connect(MSG_HANDLER_LOCAL_CONN)

        # Config the logger for the MessageClient
        message_client_log_level = os.getenv("MOVAI_MESSAGE_CLIENT_LOGS_VERBOSITY_LEVEL", 'DEBUG')
        logging.basicConfig(level=message_client_log_level)
        logging.debug(f" {msg_type} client connected to local message server on {MSG_HANDLER_LOCAL_CONN}")

    def __del__(self):
        self._socket.close()

    @property
    def robot_id(self):
        return self._robot_id

    def send_request(self, data: dict):
        """
        Wrap the data into a message request and sent it to the robot message server

        Args:
            data: The message data to be sent to the robot message server

        """
        # Add tags to the request data
        data['tags'] = {
            'fleet': self._fleet,
            'robot_id': self._robot_id,
            'robot': self._robot_name,
            'service': self._service
        }

        request_data = {
            'request': {
                'req_type': self._msg_type,
                'measurement': self._measurement,
                'req_data': data,
                'response_required': False
            }
        }
        self._send_request(request_data)

    def send_query_and_get_response(self, req_type: str, query_params: dict) -> dict:
        """
        Send a query request and return the response

        Args:
            req_type: The request type (which handler shall handle the request)
            query_params: The parameters for the query clause

        Returns: The query response

        """
        request_data = {
            'request': {
                'req_type': req_type,
                'req_data': query_params,
                'response_required': True
            }
        }
        self._send_request(request_data)
        response = self._receive_response()

        return response

    def _get_robot_info(self):
        """
        get the Robot info from the local Redis DB
        and the fleet name from an environment parameter
        """
        self._robot_id = os.getenv('DEVICE_ID')
        self._robot_name = os.getenv('DEVICE_NAME')
        self._fleet = os.getenv('FLEET_NAME', 'movai')
        self._service = os.getenv('SERVICE')

    def _send_request(self, request):
        """
        Send the message request over ZeroMQ to the local robot message server

        Args:
            request: The message request to be sent

        """
        data = json.dumps(request).encode('utf8')

        try:
            self._socket.send(data)
            logging.debug(f'Message {request}, was sent to the local message server.')
        except OSError:
            logging.error(f'OS Error! Failed to send message {request}')
        except zmq.error.Again:
            logging.error(f'ZMQ failed on timeout to send message {request}')

    def _receive_response(self) -> dict:
        """
        Receives a query response and convert it to a dictionary

        Returns: The received response as a dictionary

        """
        try:
            resp_buff = self._socket.recv()
            response = json.loads(resp_buff)
        except zmq.Again:
            response = {'status': 'ERROR - Receive Timeout'}

        return response
