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
from movai_core_shared.exceptions import ArgumentError, MessageFormatError
from movai_core_shared.envvars import (
    DEVICE_NAME,
    FLEET_NAME,
    SERVICE_NAME
)


class MessageClient:
    """
    This class is the client for message-server.
    It wraps the data into the message structure and send it to
    the message-server using ZMQClient.
    """

    def __init__(self, server_addr: str, robot_id: str = "") -> None:
        """
        constructor - initializes the object.

        Args:
            msg_type (str): The type of the message, this will affect which
            handler will be used to handle the request.

        Raises:
            TypeError: In case the supplied argument is not in the correct type.
            ArgumentError: In case the supplied argument is None or an empty string.

        """
        if not isinstance(server_addr, str):
            raise TypeError("server_addr argument must be of type string!")
        if server_addr is None or server_addr == "":
            raise ArgumentError("server_addr argument must be a non empty string!")
        self._server_addr = server_addr
        self._robot_info = {
            "fleet": FLEET_NAME,
            "robot": DEVICE_NAME,
            "service": SERVICE_NAME,
            "id": robot_id
        }
        random.seed()  # setting the seed for the random number generator
        identity = f"{DEVICE_NAME}_message_client_{random.getrandbits(24)}"
        self._zmq_client = ZMQClient(identity, self._server_addr)

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
            creation_time = time.time_ns()

        request = {
            "request": {
                "req_type": msg_type,
                "created": creation_time,
                "response_required": respose_required,
                "req_data": data,
                "robot_info": self._robot_info,
            }
        }

        self._zmq_client.send(request)
        if respose_required:
            raw_response = self._zmq_client.recieve()
            
            if not isinstance(raw_response, dict):
                raise MessageFormatError(f"The message format is unknown: {raw_response}.")
            
            if "response" in raw_response:
                response = raw_response
            else:
                response = {
                    "reponse": raw_response
                }
                
            return response
        return {}

    def foraward_request(self, request_msg: dict) -> dict:
        """forwards a request to different message-server (This function does 
        not adds the meta-data info as send_request does).

        Args:
            request_msg (dict): The request to forward.
        """
        request = {"request": request_msg}
        self._zmq_client.send(request)
        if request_msg["response_required"]:
            return self._zmq_client.recieve()
        return {}

    async def send_msg(self, data: dict, **kwargs) -> None:
        """sends a simple message as raw data, want wait for response

        Args:
            data (dict): The data to send to server.
        """
        msg = {
            "data": data
        }
        
        if "data" in kwargs:
            kwargs.pop("data")
        
        msg.update(kwargs)
        
        self._zmq_client.send(msg)