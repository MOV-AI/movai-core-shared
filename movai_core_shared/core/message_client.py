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

from movai_core_shared.consts import MESSAGE_SERVER_HOST
from movai_core_shared.core.zmq_client import ZMQClient
from movai_core_shared.exceptions import ArgumentError
from movai_core_shared.envvars import (
    DEVICE_NAME,
    FLEET_NAME,
    MESSAGE_SERVER_INTERNAL_PORT
)


class MessageClient:
    """
    This class is the client for message-server.
    It wraps the data into the message structure and send it to
    the message-server using ZMQClient.
    """

    def __init__(self,
                 server_ip: str,
                 server_port: int,
                 public_key: str,
                 robot_id: str = "") -> None:
        """
        constructor - initializes the object.

        Args:
            msg_type (str): The type of the message, this will affect which
            handler will be used to handle the request.

        Raises:
            TypeError: In case the supplied argument is not in the correct type.
            ArgumentError: In case the supplied argument is None or an empty string.

        """
        if not isinstance(server_ip, str):
            raise TypeError("server_ip argument must be of type string!")
        if server_ip is None or server_ip == "":
            raise ArgumentError("server_ip argument must be a non empty string!")
        if not isinstance(server_port, int):
            raise TypeError("server_port argument must be of type integer!")
        if server_port is None or server_port == 0:
            raise ArgumentError("server_port argument must be a non zero integer!")
        if not isinstance(public_key, str):
            raise TypeError("public_key argument must be of type string!")
        public_key = public_key
        self._robot_info = {
            "fleet_name": FLEET_NAME,
            "robot_name": DEVICE_NAME,
            "robot_id": robot_id
        }
        random.seed()  # setting the seed for the random number generator
        identity = f"{DEVICE_NAME}_message_client_{random.getrandbits(24)}"
        self._zmq_client = ZMQClient(server_ip, server_port, public_key, identity)

    def send_request(self,
                     msg_type: str,
                     data: dict,
                     creation_time: str = None,
                     respose_required: bool = False
    ) -> dict:
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
            "request": {
                "req_type": msg_type,
                "created": creation_time,
                "response_required": respose_required,
                "req_data": data,
                "robot_info": self._robot_info,
            }
        }

        self._zmq_client.send_msg(request)
        if respose_required:
            return self._zmq_client.rcv_msg()
        return {}

    def foraward_request(self, request_msg: dict) -> None:
        """forwards a request to different message-server (This function does 
        not adds the meta-data info as send_request does).

        Args:
            request_msg (dict): The request to forward.
        """
        request = {"request": request_msg}
        self._zmq_client.send_msg(request)

    @staticmethod
    def get_local_message_client(robot_id: str):
        """Returns an MessageClient object configured to connect 
        to the local message-server

        Args:
            robot_id (str): The robot id of the client.

        Returns:
            MessageClient: A MessageClient object.
        """
        try:
            client = MessageClient(MESSAGE_SERVER_HOST,
                                   MESSAGE_SERVER_INTERNAL_PORT,
                                   "",
                                   robot_id)
            return client
        except Exception:
            return None
