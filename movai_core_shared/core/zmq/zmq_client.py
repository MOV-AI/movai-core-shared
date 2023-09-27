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

    def _init_lock(self) -> None:
        """Initializes the lock."""
        self._lock = threading.Lock()

    def init_socket(self) -> None:
        """Initializes the socket and connect to the server."""
        self._init_lock()
        self._socket = self._context.socket(zmq.DEALER)
        self._socket.setsockopt(zmq.IDENTITY, self._identity)
        self._socket.setsockopt(zmq.RCVTIMEO, int(MOVAI_ZMQ_RECV_TIMEOUT_MS))
        self._socket.setsockopt(zmq.SNDTIMEO, int(MOVAI_ZMQ_SEND_TIMEOUT_MS))
        self._socket.connect(self._addr)

    def send(self, msg: dict) -> None:
        """
        Synchronously sends a message to the server.
        
        Args:
            data (dict): the msg representation
        """
        try:
            data = create_msg(msg)
            with self._lock:
                self._socket.send(data)
        except Exception as exc:
            if self._lock.locked():
                self._lock.release()
            self._logger.error("%s failed to send message, got exception of type %s", self.__class__.__name__, exc)

    def recieve(self) -> dict:
        """
        Synchronously recieves data from the server.

        Returns:
            (dict): A response from the server.
        """
        try:
            buffer = None
            self._lock.acquire()
            with self._lock:
                buffer = self._socket.recv_multipart()
            response = extract_reponse(buffer)
            return response
        except Exception as exc:
            if self._lock.locked():
                self._lock.release()
            self._logger.error("%s failed to recieve data, got error of type: %s", self.__class__.__name__, exc)
            return {}

class AsyncZMQClient(ZMQClient):
    """An Async implementation of ZMQ Client"""
    _context = zmq.asyncio.Context()

    def _init_lock(self) -> None:
        """Initializes the lock."""
        self._lock = asyncio.Lock()

    async def send(self, msg: dict) -> None:
        """
        Asynchrounously send the message to the server.

        Args:
            data (bytes): the msg representation
        """
        try:
            data = create_msg(msg)
            async with self._lock:
                await self._socket.send(data)
        except Exception as exc:
            if self._lock.locked():
                await self._lock.release()
            self._logger.error("%s failed to send message, got exception of type %s", self.__class__.__name__, exc)
    
    async def recieve(self) -> dict:
        """
        Asynchrounsly recieves data from the server.

        Returns:
            (dict): A response from the server.
        """
        try:
            buffer = None
            async with self._lock:
                buffer = await self._socket.recv_multipart()
            response = extract_reponse(buffer)
            return response
        except Exception as exc:
            if self._lock.locked():
                await self._lock.release()
            self._logger.error("%s failed to recieve data, got error of type: %s", self.__class__.__name__, exc)
            return {}
