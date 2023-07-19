"""
   Copyright (C) Mov.ai  - All Rights Reserved
   Unauthorized copying of this file, via any medium is strictly prohibited
   Proprietary and confidential

   Usage:
        Basic 0MQ client for connecting 0MQ servers.

   Developers:
   - Erez Zomer (erez@mov.ai) - 2022
"""
import asyncio
import json
import threading
from logging import getLogger

import zmq
import zmq.asyncio

from movai_core_shared.envvars import MOVAI_ZMQ_TIMEOUT_MS
from movai_core_shared.exceptions import MessageError


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
        self._zmq_ctx = None
        self._lock = None
        self.prepare_socket()

    def _init_context(self):
        self._zmq_ctx = zmq.Context()

    def _init_lock(self):
        self._lock = threading.Lock()

    def prepare_socket(self):
        """Creates the socket and sets a lock."""
        self._init_context()
        self._socket = self._zmq_ctx.socket(zmq.DEALER)
        self._socket.setsockopt(zmq.IDENTITY, self._identity)
        self._socket.setsockopt(zmq.SNDTIMEO, int(MOVAI_ZMQ_TIMEOUT_MS))
        self._socket.connect(self._addr)
        self._init_lock()

    def __del__(self):
        """closes the socket when the object is destroyed."""
        # Close all sockets associated with this context and then terminate the context.
        self._socket.close()
        self._zmq_ctx.term()

    def _send(self, msg: bytes):
        """sends a message in a synchronous way."""
        with self._lock:
            self._socket.send(msg)

    def _create_msg(self, msg: dict):
        """Extracts the msg from

        Args:
            msg (dict): _description_

        Returns:
            _type_: _description_
        """
        if not isinstance(msg, dict):
            return
        try:
            data = json.dumps(msg).encode("utf8")
            return data
        except (json.JSONDecodeError, TypeError) as error:
            self._logger.error(
                f"Got error of type {error.__class__.__name__} while trying to send the message"
            )

    def send(self, msg: dict) -> None:
        """
        Send the message request over ZeroMQ to the local robot message server.

        Args:
            msg (dict): The message request to be sent
        """
        data = self._create_msg(msg)
        self._send(data)

    def _recieve(self):
        """Synchrounsly recieves data from the server.

        Returns:
            (bytes): raw data from the server.
        """
        with self._lock:
            buffer = self._socket.recv_multipart()
        return buffer

    def _extract_reponse(self, buffer: bytes):
        """Extracts the response from the buffer.

        Args:
            buffer (bytes): The memory buffer which contains the reponse msg.

        Returns:
            (dict): A reponse from server.
        """
        index = len(buffer) - 1
        msg = buffer[index]

        if msg is None:
            raise MessageError("Got an empty msg!")

        try:
            response = json.loads(msg)
            return response
        except (json.JSONDecodeError, TypeError) as error:
            self._logger.error(
                f"Got error of type {error.__class__.__name__} while trying to recieve the message."
            )
            return {}

    def recieve(self) -> dict:
        """
        Recieves a message response over ZeroMQ from the server.

        Raises:
            MessageError: In case response is empty.

        Returns:
            dict: The response from the server.
        """
        buffer = self._recieve()
        response = self._extract_reponse(buffer)
        return response


class AsyncZMQClient(ZMQClient):
    """An Async implementation of ZMQ Client"""

    def _init_context(self):
        self._zmq_ctx = zmq.asyncio.Context()

    def _init_lock(self):
        self._lock = asyncio.Lock()

    async def _send(self, msg: bytes):
        """Asynchrounously send the message.

        Args:
            data (bytes): the msg representation
        """
        async with self._lock:
            await self._socket.send(msg)

    async def send(self, msg: dict) -> None:
        """
        Send the message request over ZeroMQ to the local robot message server.

        Args:
            msg (dict): The message request to be sent
        """
        data = self._create_msg(msg)
        await self._send(data)

    async def _recieve(self):
        """Asynchrounsly recieves data from the server.

        Returns:
            (bytes): raw data from the server.
        """
        async with self._lock:
            buffer = await self._socket.recv_multipart()
            return buffer

    async def recieve(self) -> dict:
        """
        Recieves a message response over ZeroMQ from the server.

        Raises:
            MessageError: In case response is empty.

        Returns:
            dict: The response from the server.
        """
        buffer = await self._recieve()
        response = self._extract_reponse(buffer)
        return response
