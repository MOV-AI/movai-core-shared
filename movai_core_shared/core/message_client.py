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

from movai_core_shared.core.zmq_client import ZMQClient, AsyncZMQClient
from movai_core_shared.envvars import DEVICE_NAME, FLEET_NAME, SERVICE_NAME
from movai_core_shared.exceptions import ArgumentError, MessageFormatError


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
            "id": robot_id,
        }
        random.seed()  # setting the seed for the random number generator
        identity = f"{DEVICE_NAME}_message_client_{random.getrandbits(24)}"
        self._zmq_client = None
        self._init_zmq_client(identity)

    def _init_zmq_client(self, identity: str):
        """initializes the ZMQClient object

        Args:
            identity (str): A string represent unique identity for the client.
        """
        self._zmq_client = ZMQClient(identity, self._server_addr)

    def _build_request(
        self, msg_type: str, data: dict, creation_time: str = None, respose_required: bool = False
    ) -> dict:
        """Build a request in the format accepted by the message server.

        Args:
            msg_type (str): The type of the message (logs, alerts, metrics....)
            data (dict): The data to include in the request.
            creation_time (str, optional): The time the request was created.
            respose_required (bool, optional): Tells the message-server if the client is wainting for response.

        Returns:
            {dict}: The message request to send the message-server
        """
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
        return request

    def _extract_response(self, msg) -> dict:
        """Extracts the reponse from the message.

        Args:
            msg (msg): The msg got from message-server.

        Raises:
            MessageFormatError: in case the message is not in the acceptable format.

        Returns:
            (dict): The actual response
        """
        if not isinstance(msg, dict):
            raise MessageFormatError(f"The message format is unknown: {msg}.")

        if "response" in msg:
            response = msg
        else:
            response = {"response": msg}

        return response

    def send_request(
        self, msg_type: str, data: dict, creation_time: str = None, respose_required: bool = False
    ) -> dict:
        """
        Wrap the data into a message request and sent it to the robot message server

        Args:
            data (dict): The message data to be sent to the robot message server.
            creation_time (str): The time where the request is created.
        """
        # Add tags to the request data
        request = self._build_request(msg_type, data, creation_time, respose_required)

        self._zmq_client.send(request)
        if respose_required:
            msg = self._zmq_client.recieve()
            response = self._extract_response(msg)
            return response

        return {}

    def foraward_request(self, request_msg: dict) -> dict:
        """forwards a request to different message-server (This function does
        not adds the meta-data info as send_request does).

        Args:
            request_msg (dict): The request to forward.
        """
        if "request" not in request_msg:
            request = {"request": request_msg}
        self._zmq_client.send(request)
        response_required = request_msg.get("response_required")

        if response_required:
            response = self._zmq_client.recieve()
            return response
        return {}

    async def send_msg(self, data: dict, **kwargs) -> None:
        """sends a simple message as raw data, won't wait for response

        Args:
            data (dict): The data to send to server.
        """
        msg = {"data": data}

        if "data" in kwargs:
            kwargs.pop("data")

        msg.update(kwargs)

        self._zmq_client.send(msg)


class AsyncMessageClient(MessageClient):
    def _init_zmq_client(self, identity: str):
        self._zmq_client = AsyncZMQClient(identity, self._server_addr)

    async def send_request(
        self, msg_type: str, data: dict, creation_time: str = None, respose_required: bool = False
    ) -> dict:
        """
        Wrap the data into a message request and sent it asynchonously to the robot message server
        (can not wait for a response).

        Args:
            data (dict): The message data to be sent to the robot message server.
            creation_time (str): The time where the request is created.
        """
        request = self._build_request(msg_type, data, creation_time, respose_required)

        await self._zmq_client.send(request)
        if respose_required:
            msg = await self._zmq_client.recieve()
            response = self._extract_response(msg)
            return response

        return {}

    async def foraward_request(self, request_msg: dict) -> dict:
        """
        Send the request asynchrounsly to different message-server (This function does
        not adds the meta-data info as send_request does).

        Args:
            request_msg (dict): The request to forward.
        """
        if "request" not in request_msg:
            request = {"request": request_msg}
        await self._zmq_client.send(request)

        response_required = request_msg.get("response_required")
        if response_required is None:
            raise MessageFormatError("The field response_required is missing from request message")

        if response_required:
            response = await self._zmq_client.recieve()
            return response
        return {}

    async def send_msg(self, data: dict, **kwargs) -> None:
        """sends a simple message as raw data asynchrously, won't wait for response

        Args:
            data (dict): The data to send to server.
        """
        msg = {"data": data}

        if "data" in kwargs:
            kwargs.pop("data")

        msg.update(kwargs)

        await self._zmq_client.send(msg)
