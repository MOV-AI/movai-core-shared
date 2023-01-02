"""
   Copyright (C) Mov.ai  - All Rights Reserved
   Unauthorized copying of this file, via any medium is strictly prohibited
   Proprietary and confidential

   Usage:
        Basic 0MQ client for connecting 0MQ servers.

   Developers:
   - Erez Zomer (erez@mov.ai) - 2022
"""
import json
import zmq.asyncio
import zmq

from movai_core_shared.envvars import MOVAI_ZMQ_TIMEOUT_MS
from movai_core_shared.exceptions import MessageError, MessageFormatError

class ZMQClient:
    """Basic ZMQ Client
    """
    def __init__(self, identity: str, server: str) -> None:
        # ZMQ settings:
        self._identity = identity.encode("utf-8")
        zmq_ctx = zmq.Context()
        self._socket = zmq_ctx.socket(zmq.DEALER)
        self._socket.setsockopt(zmq.IDENTITY, self._identity)
        self._socket.setsockopt(zmq.SNDTIMEO, int(MOVAI_ZMQ_TIMEOUT_MS))
        self._socket.connect(server)

    def __del__(self):
        """closes the socket when the object is destroyed.
        """
        self._socket.close()

    def send(self, msg: dict) -> None:
        """
        Send the message request over ZeroMQ to the local robot message server

        Args:
            msg (dict): The message request to be sent

        """
        try:
            data = json.dumps(msg).encode('utf8')
        except json.JSONDecodeError as error:
            raise MessageError(f"Failed to decode message: {msg}") from error

        self._socket.send(data)

    def recieve(self) -> dict:
        """
        Recieves a message response over ZeroMQ from the server.

        Raises:
            MessageFormatError: In case the response message format is wrong.

        Returns:
            dict: The response from the server.
        
        Raises:
            MessageError: In case response is empty.
        """
        response = self._socket.recv_multipart()
        index = len(response) - 1
        buffer = response[index]

        if buffer is None:
            raise MessageError("Got an empty response!")

        msg = json.loads(buffer)
        # check for request in request
        if "response" not in msg:
            raise MessageFormatError(f"The message format is unknown: {msg}.")
        response_msg = msg["response"]
        return response_msg
