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
from logging import getLogger
import threading
import zmq.asyncio
import zmq

from movai_core_shared.envvars import MOVAI_ZMQ_TIMEOUT_MS
from movai_core_shared.exceptions import MessageError, MessageFormatError


class ZMQClient:
    """A very basic implementation of ZMQ Client"""

    def __init__(self, identity: str, server_addr: str) -> None:
        """Initializes the object and the connection to the serrver.

        Args:
            identity (str): A unique idenetity which will be used by
                the server to identify the client.
            server (str): The server addr and port in the form:
                'tcp://server_addr:port'
        """
        self._logger = getLogger(self.__class__.__name__)
        self._identity = identity.encode("utf-8")
        self._addr = server_addr
        self.zmq_ctx = zmq.asyncio.Context()
        self._socket = self.zmq_ctx.socket(zmq.DEALER)
        self._socket.setsockopt(zmq.IDENTITY, self._identity)
        self._socket.setsockopt(zmq.SNDTIMEO, int(MOVAI_ZMQ_TIMEOUT_MS))
        self._socket.connect(self._addr)
        self.lock = threading.Lock()

    def __del__(self):
        """closes the socket when the object is destroyed."""
        # Close all sockets associated with this context and then terminate the context.
        self._socket.close()
        self.zmq_ctx.term()

    async def send(self, msg: dict) -> None:
        """
        Send the message request over ZeroMQ to the local robot message server.

        Args:
            msg (dict): The message request to be sent
        """
        if not isinstance(msg, dict):
            return
        try:
            data = json.dumps(msg).encode("utf8")
            with self.lock:
                await self._socket.send(data)
        except (json.JSONDecodeError, TypeError) as error:
            self._logger.error(
                f"Got error of type {error.__class__.__name__} while trying to send message"
            )

    async def recieve(self) -> dict:
        """
        Recieves a message response over ZeroMQ from the server.

        Raises:
            MessageFormatError: In case the response message format is wrong.
            MessageError: In case response is empty.

        Returns:
            dict: The response from the server.
        """
        with self.lock:
            response = await self._socket.recv_multipart()
        index = len(response) - 1
        buffer = response[index]

        if buffer is None:
            raise MessageError("Got an empty response!")

        msg = json.loads(buffer)

        return msg
