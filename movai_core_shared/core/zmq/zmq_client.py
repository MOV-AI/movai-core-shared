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
import threading
from logging import getLogger

import zmq
import zmq.asyncio

from movai_core_shared.core.zmq.zmq_base import ZMQBase
from movai_core_shared.core.zmq.zmq_helpers import create_msg, extract_reponse
from movai_core_shared.envvars import MOVAI_ZMQ_SEND_TIMEOUT_MS, MOVAI_ZMQ_RECV_TIMEOUT_MS
from movai_core_shared.exceptions import MessageError


class ZMQClient(ZMQBase):
    """A very basic implementation of ZMQ Client"""

    def init_socket(self):
        """Creates the socket and sets a lock."""
        self._lock = threading.Lock()
        self._socket = self._context.socket(zmq.DEALER)
        self._socket.setsockopt(zmq.IDENTITY, self._identity)
        self._socket.setsockopt(zmq.RCVTIMEO, int(MOVAI_ZMQ_RECV_TIMEOUT_MS))
        self._socket.setsockopt(zmq.SNDTIMEO, int(MOVAI_ZMQ_SEND_TIMEOUT_MS))
        self._socket.connect(self._addr)

    def send(self, msg: bytes):
        """sends a message in a synchronous way."""
        data = create_msg(msg)
        self._lock.acquire()
        try:
            self._socket.send(data)
        except Exception as exc:
            self._logger.error("%s failed to send message, got exception of type %s", self.__class__.__name__, exc)
        finally:
            self._lock.release()

    def recieve(self):
        """Synchronously recieves data from the server.

        Returns:
            (bytes): raw data from the server.
        """
        self._lock.acquire()
        buffer = None
        try:
            buffer = self._socket.recv_multipart()
            if not buffer:
                return {}
            response = extract_reponse(buffer)
            return response
        except Exception as exc:
            self._logger.error("%s failed to recieve data, got error of type: %s", self.__class__.__name__, exc)
        finally:
            self._lock.release()

class AsyncZMQClient(ZMQClient):
    """An Async implementation of ZMQ Client"""
    _context = zmq.asyncio.Context()

    def init_socket(self):
        """Creates the socket and sets a lock."""
        super().init_socket()
        self._lock = asyncio.Lock()

    async def send(self, msg: dict):
        """Asynchrounously send the message.

        Args:
            data (bytes): the msg representation
        """
        try:
            data = create_msg(msg)
            await self._socket.send(data)
        except Exception as exc:
            self._logger.error("%s failed to send message, got exception of type %s", self.__class__.__name__, exc)

    async def recieve(self):
        """Asynchrounsly recieves data from the server.

        Returns:
            (bytes): raw data from the server.
        """
        buffer = None
        try:
            buffer = await self._socket.recv_multipart()
            if not buffer:
                return {}
            response = extract_reponse(buffer)
            return response
        except Exception as exc:
            self._logger.error("%s failed to recieve data, got error of type: %s", self.__class__.__name__, exc)
        return buffer
