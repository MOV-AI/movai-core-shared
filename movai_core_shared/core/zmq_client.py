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
        self._lock = None
        self.prepare_socket()
        self._init_lock()

    def _init_context(self):
        self._zmq_ctx = zmq.Context()

    def _init_lock(self):
        self._lock = threading.Lock()

    def prepare_socket(self):
        """Creates the socket and sets a lock."""
        self._init_context()
        self._socket = self._zmq_ctx.socket(zmq.DEALER)
        self._socket.setsockopt(zmq.IDENTITY, self._identity)
        self._socket.setsockopt(zmq.RCVTIMEO, int(MOVAI_ZMQ_TIMEOUT_MS))
        self._socket.setsockopt(zmq.SNDTIMEO, int(MOVAI_ZMQ_TIMEOUT_MS))
        self._socket.connect(self._addr)

    def __del__(self):
        """closes the socket when the object is destroyed."""
        # Close all sockets associated with this context and then terminate the context.
        self._socket.close()
        self._zmq_ctx.term()

    def _send(self, msg: bytes):
        """sends a message in a synchronous way."""
        self._lock.acquire()
        try:
            self._socket.send(msg)
        except:
            self._logger.error("Failed to send message")
        finally:
            self._lock.release()

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
        self._lock.acquire()
        buffer = None
        try:
            buffer = self._socket.recv_multipart()
        except Exception as e:
            self._logger.error("error while trying to recieve data, %s", e)
        finally:
            self._lock.release()
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
        self._zmq_ctx = zmq.asyncio.Context()

    def _init_lock(self):
        pass

    async def _send(self, msg: bytes):
        """Asynchrounously send the message.

        Args:
            data (bytes): the msg representation
        """
        await self._lock.acquire()
        try:
            await self._socket.send(msg)
        except Exception as e:
            self._logger.error("error while trying to recieve data, %s", e)
        finally:
            self._lock.release()

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
        await self._lock.acquire()
        try:
            buffer = await self._socket.recv_multipart()
        except Exception as e:
            self._logger.error("error while trying to recieve data, %s", e)
        finally:
            self._lock.release()
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
