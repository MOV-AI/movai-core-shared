"""
   Copyright (C) Mov.ai  - All Rights Reserved
   Unauthorized copying of this file, via any medium is strictly prohibited
   Proprietary and confidential

   Usage:
        Basic 0MQ client for connecting 0MQ servers.

   Developers:
   - Erez Zomer (erez@mov.ai) - 2022
"""
from typing import List
import asyncio
import json
from logging import getLogger

import zmq
import zmq.asyncio

from movai_core_shared.envvars import MOVAI_ZMQ_TIMEOUT_MS
from movai_core_shared.exceptions import MessageError


class ZMQClient:
    """A very basic implementation of ZMQ Client"""

    def __init__(self, identity: str, server_addr: str) -> None:
        """Initializes the object and the connection to the server.

        Args:
            identity (str): A unique identity which will be used by
                the server to identify the client.
            server_addr (str): The server addr and port in the form:
                'tcp://server_addr:port'
        """
        self._logger = getLogger(self.__class__.__name__)
        self._identity = identity.encode("utf-8")
        self._addr = server_addr
        self._zmq_ctx = None
        self._init_context()

    def _init_context(self):
        self._zmq_ctx = zmq.Context()

    def prepare_socket(self) -> zmq.Socket:
        """Creates the socket and sets a lock."""
        socket = self._zmq_ctx.socket(zmq.DEALER)
        socket.setsockopt(zmq.IDENTITY, self._identity)
        socket.setsockopt(zmq.RCVTIMEO, int(MOVAI_ZMQ_TIMEOUT_MS))
        socket.setsockopt(zmq.SNDTIMEO, int(MOVAI_ZMQ_TIMEOUT_MS))
        socket.connect(self._addr)
        return socket

    def __del__(self):
        """closes the socket when the object is destroyed."""
        # Close all sockets associated with this context and then terminate the context.
        self._zmq_ctx.term()

    def _create_msg(self, msg: dict):
        """Extracts the msg from
        Args:
            msg (dict): _description_
        Returns:
            json string
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

    def send(self, msg: dict, response_required: bool = False) -> dict:
        """
        Send the message request over ZeroMQ to the local robot message server.

        Args:
            msg (dict): The message request to be sent
            response_required (bool): if socket will wait for a response, Default False
        """
        data = self._create_msg(msg)
        socket = self.prepare_socket()
        socket.send(data)
        if response_required:
            buffer = socket.recv_multipart()
            response = self._extract_response(buffer)
        else:
            response = {}
        socket.close()
        return response

    def _extract_response(self, buffer: List[bytes]):
        """Extracts the response from the buffer.

        Args:
            buffer (bytes): The memory buffer which contains the response msg.

        Returns:
            (dict): A response from server.
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


class AsyncZMQClient(ZMQClient):
    """An Async implementation of ZMQ Client"""

    def __init__(self, identity: str, server_addr: str) -> None:
        """Initializes the object and the connection to the server.

        Args:
            identity (str): A unique identity which will be used by
            server_addr (str): The server addr and port
        """
        super().__init__(identity, server_addr)
        self._lock = asyncio.Lock()
        self._init_context()
        self._socket = self.prepare_socket()

    def _init_context(self):
        self._zmq_ctx = zmq.asyncio.Context()

    async def send(self, msg: dict, response_required: bool = False) -> dict:
        """
        Send the message request over ZeroMQ to the local robot message server.

        Args:
            msg (dict): The message request to be sent
            response_required (bool): Will wait for response, Default False
        """
        data = self._create_msg(msg)
        async with self._lock:
            await self._socket.send(data)
        if response_required:
            response = await self._receive()
        else:
            response = {}
        return response

    async def _receive(self) -> dict:
        """
        Receives a message response over ZeroMQ from the server.
        Raises:
            MessageError: In case response is empty.
        Returns:
            dict: The response from the server.
        """
        async with self._lock:
            buffer = await self._socket.recv_multipart()
        response = self._extract_response(buffer)
        return response
