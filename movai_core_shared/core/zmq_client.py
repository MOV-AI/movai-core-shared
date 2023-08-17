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
from movai_core_shared.core.zmq_base import ZMQBase


class ZMQClient(ZMQBase):
    """A very basic implementation of ZMQ Client"""

    def __init__(self, identity: str, server_addr: str, client_type: zmq.TYPE = zmq.DEALER) -> None:
        """Initializes the object and the connection to the server.

        Args:
            identity (str): A unique identity which will be used by
                the server to identify the client.
            server_addr (str): The server addr and port in the form:
                'tcp://server_addr:port'
        """
        super().__init__(identity, server_addr)
        self.prepare_socket(client_type)

    def _init_context(self):
        if self._ctx is None:
            self._ctx = zmq.Context()

    def _init_socket(self, client_type: zmq.TYPE):
        self._socket = self._ctx.socket(client_type)

    def _init_lock(self):
        self._lock = threading.Lock()

    def prepare_socket(self, client_type: zmq.TYPE):
        """Creates the socket and sets a lock."""
        self._init_context()
        self._init_socket(client_type)
        self._socket.setsockopt(zmq.IDENTITY, self._identity)
        self._socket.setsockopt(zmq.RCVTIMEO, 5 * int(MOVAI_ZMQ_TIMEOUT_MS))
        self._socket.setsockopt(zmq.SNDTIMEO, int(MOVAI_ZMQ_TIMEOUT_MS))
        self._socket.connect(self._addr)

    def __del__(self):
        """closes the socket when the object is destroyed."""
        # Close all sockets associated with this context and then terminate the context.
        if self._socket is not None:
            self._socket.close()

    def _send(self, msg: bytes):
        """sends a message in a synchronous way."""
        try:
            self._socket.send(msg)
        except:
            self._logger.error("Failed to send message")

    def _create_msg(self, msg: dict):
        """create the msg in json format.

        Args:
            msg (dict): A dictionary format of the messge.

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

    def send(self, msg: dict) -> None:
        """
        Send the message request over ZeroMQ to the local robot message server.

        Args:
            msg (dict): The message request to be sent
        """
        data = self._create_msg(msg)
        self._send(data)

    def _recieve(self):
        """Synchronously recieves data from the server.

        Returns:
            (bytes): raw data from the server.
        """
        buffer = None
        try:
            buffer = self._socket.recv_multipart()
        except Exception as e:
            self._logger.error("error while trying to recieve data, %s", e)
        return buffer

    def _extract_reponse(self, buffer: bytes):
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

    def recieve(self) -> dict:
        """
        Recieves a message response over ZeroMQ from the server.

        Raises:
            MessageError: In case response is empty.

        Returns:
            dict: The response from the server.
        """
        buffer = self._recieve()
        if not buffer:
            return {}
        response = self._extract_reponse(buffer)
        return response


class AsyncZMQClient(ZMQClient):
    """An Async implementation of ZMQ Client"""

    def _init_context(self):
        self._ctx = zmq.asyncio.Context()

    def _init_lock(self):
        self._lock = asyncio.Lock()

    async def _send(self, msg: bytes):
        """Asynchrounously send the message.

        Args:
            data (bytes): the msg representation
        """
        try:
            await self._socket.send(msg)
        except Exception as e:
            self._logger.error("error while trying to recieve data, %s", e)

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
        buffer = None
        try:
            buffer = await self._socket.recv_multipart()
        except Exception as e:
            self._logger.error("error while trying to recieve data, %s", e)
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
        if not buffer:
            return {}
        response = self._extract_reponse(buffer)
        return response


class REQZMQClient(ZMQClient):
    def _init_socket(self):
        self._socket = self._ctx.socket(zmq.REQ)
