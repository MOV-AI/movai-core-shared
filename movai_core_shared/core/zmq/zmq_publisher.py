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
import zmq
import zmq.asyncio

from movai_core_shared.core.zmq.zmq_base import ZMQBase
from movai_core_shared.core.zmq.zmq_helpers import create_msg
from movai_core_shared.envvars import MOVAI_ZMQ_SEND_TIMEOUT_MS


class ZMQPublisher(ZMQBase):
    """A very basic implementation of ZMQ publisher"""

    def init_socket(self):
        """Creates the socket and sets a lock."""
        self._lock = threading.Lock()
        self._socket = self._context.socket(zmq.PUB)
        self._socket.setsockopt(zmq.IDENTITY, self._identity)
        self._socket.setsockopt(zmq.SNDTIMEO, int(MOVAI_ZMQ_SEND_TIMEOUT_MS))
        self._socket.bind(self._addr)
        self._logger.info(f"{self.__class__.__name__} is listening on: {self._addr}")

    def publish(self, topic: str, msg: dict) -> None:
        """
        Send the message request over ZeroMQ to the local robot message server.

        Args:
            msg (dict): The message request to be sent
        """
        data = create_msg(msg)
        with self._lock:
            try:
                self._socket.send(data)
            except Exception as exc:
                self._logger.error(f"Got {exc} when trying to send message.")


class AsyncZMQPublisher(ZMQPublisher):
    """An Async implementation of ZMQ Publisher"""
    _context = zmq.asyncio.Context()
    
    def __init__(self, identity: str, bind_addr: str) -> None:
        super().__init__(identity, bind_addr)
        self._lock = asyncio.Lock()

    def init_socket(self):
        """Creates the socket and sets a lock."""
        self._lock = asyncio.Lock()
        self._socket = self._context.socket(zmq.PUB)
        self._socket.setsockopt(zmq.IDENTITY, self._identity)
        self._socket.setsockopt(zmq.SNDTIMEO, int(MOVAI_ZMQ_SEND_TIMEOUT_MS))
        self._socket.bind(self._addr)
        self._logger.info(f"{self.__class__.__name__} is bounded to: {self._addr}")

    async def publish(self, topic: str, msg: dict) -> None:
        """
        Send the message over ZeroMQ subscribers.

        Args:
            msg (dict): The message to be sent
        """
        data = create_msg(msg)
        with self._lock:
            try:
                await self._socket.send(data)
            except Exception as exc:
                self._logger.error(f"Got {exc} when trying to send message.")