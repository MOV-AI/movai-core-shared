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
from movai_core_shared.core.zmq.zmq_helpers import extract_reponse


class ZMQSubscriber(ZMQBase):
    """A very basic implementation of ZMQ Subscriber"""

    def _init_lock(self) -> None:
        """Initializes the lock."""
        self._lock = threading.Lock()

    def init_socket(self) -> None:
        """Initializes the socket and set options."""
        self._init_lock()
        self._socket: zmq.Socket = self._context.socket(zmq.SUB)
        self._socket.setsockopt(zmq.IDENTITY, self._identity)
        self.subscribe(b"", self._addr)

    def subscribe(self, topic: str, pub_addr: str) -> None:
        """
        Adds a topic to subscribe to.

        Args:
            topic (str): The name of the topic to subscribe.
            pub_addr (str): The address of the publisher.
        """
        if isinstance(topic, str):
            self._socket.setsockopt_string(zmq.SUBSCRIBE, topic)
        elif isinstance(topic, bytes):
            self._socket.setsockopt(zmq.SUBSCRIBE, b"")
        self._socket.connect(pub_addr)

    def recieve(self, use_lock: bool = False) -> dict:
        """
        Synchronously recieves data from the server.

        Returns:
            (dict): raw data from the server.
        """
        try:
            if use_lock and self._lock:
                self._lock.acquire()
                buffer = self._socket.recv_multipart()
                self._lock.release()
            else:
                buffer = self._socket.recv_multipart()
            response = extract_reponse(buffer)
            return response
        except Exception as exc:
            if self._lock and self._lock.locked():
                self._lock.release()
            self._logger.error(
                f"{self.__class__.__name__} failed to recieve data, got error of type: {exc}"
            )
            return {}


class AsyncZMQSubscriber(ZMQSubscriber):
    """An Async implementation of ZMQ subscriber"""

    _context = zmq.asyncio.Context()

    def _init_lock(self) -> None:
        """Initializes the lock."""
        self._lock = asyncio.Lock()

    async def recieve(self, use_lock: bool = False) -> dict:
        """
        Asynchrounsly recieves data from the server.

        Returns:
            (dict): raw data from the server.
        """
        try:
            if use_lock and self._lock:
                await self._lock.acquire()
                buffer = await self._socket.recv_multipart()
                self._lock.release()
            else:
                buffer = await self._socket.recv_multipart()
            response = extract_reponse(buffer)
            return response
        except Exception as exc:
            if self._lock and self._lock.locked():
                self._lock.release()
            self._logger.error(
                f"{self.__class__.__name__} failed to recieve data, got error of type: {exc}"
            )
            return {}
