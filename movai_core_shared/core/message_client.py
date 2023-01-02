"""
   Copyright (C) Mov.ai  - All Rights Reserved
   Unauthorized copying of this file, via any medium is strictly prohibited
   Proprietary and confidential

   Usage:
        Sends messages to the robot Message-Server.

   Developers:
   - Ofer Katz (ofer@mov.ai) - 2022
   - Erez Zomer (erez@mov.ai) - 2022
"""
import random
import time

from movai_core_shared.core.zmq_client import ZMQClient
from movai_core_shared.exceptions import ArgumentError
from movai_core_shared.envvars import (
    MESSAGE_SERVER_LOCAL_ADDR,
    DEVICE_NAME,
    FLEET_NAME
)



class MessageClient:
    """
    This class is the client for message-server.
    It wraps the data into the message structure and send it to
    the message-server using ZMQClient.
    """
    def __init__(self, msg_type: str) -> None:
        """
        constructor - initializes the object.

        Args:
            msg_type (str): The type of the message, this will affect which
            handler will be used to handle the request.
        
        Raises:
            TypeError: In case the supplied argument is not in the correct type.
            ArgumentError: In case the supplied argument is None or an empty string.

        """
        if not isinstance(msg_type, str):
            raise TypeError("msg_type argument must be of type string!")
        if msg_type is None or msg_type == "":
            raise ArgumentError("msg_type argument must be a non empty string!")
        self._msg_type = msg_type
        #TODO: find a solution to import robot id without activating the logger.
        self._robot_id = str(random.getrandbits(24))
        self._robot_name = DEVICE_NAME
        self._fleet = FLEET_NAME
        self._robot_info = {
            'fleet_name': self._fleet,
            'robot_name': self._robot_name,
            'robot_id': self._robot_id
        }
        random.seed() # setting the seed for the random number generator
        identity = f"{msg_type}_message_client_{random.getrandbits(24)}"
        self._zmq_client = ZMQClient(identity, MESSAGE_SERVER_LOCAL_ADDR)

    def send_request(self, data: dict, creation_time: str = None, respose_required: bool = False) -> dict:
        """
        Wrap the data into a message request and sent it to the robot message server

        Args:
            data (dict): The message data to be sent to the robot message server.
            creation_time (str): The time where the request is created.
        """
        # Add tags to the request data

        if creation_time is None:
            creation_time = time.time()

        request = {
            'request': {
                'req_type': self._msg_type,
                'created': creation_time,
                "response_required": respose_required,
                'req_data': data,
                'robot_info': self._robot_info
            }
        }

        self._zmq_client.send(request)
        if respose_required:
            return self._zmq_client.recieve()
        return {}
