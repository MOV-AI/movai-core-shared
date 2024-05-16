"""
   Copyright (C) Mov.ai  - All Rights Reserved
   Unauthorized copying of this file, via any medium is strictly prohibited
   Proprietary and confidential

   Usage:
        Basic 0MQ client for connecting 0MQ servers.

   Developers:
   - Erez Zomer (erez@mov.ai) - 2023
"""
import zmq
import zmq.asyncio

from movai_core_shared.core.zmq.zmq_base import ZMQBase
from movai_core_shared.core.zmq.zmq_helpers import extract_reponse


class ZMQSubscriber(ZMQBase):
    """A very basic implementation of ZMQ Subscriber"""

    def init_socket(self) -> None:
        """Initializes the socket and set options."""
        self._init_lock()
        self._socket: zmq.Socket = self._context.socket(zmq.SUB)
        self._socket.setsockopt(zmq.IDENTITY, self._identity)
        self._socket.setsockopt_string(zmq.SUBSCRIBE, "")
        self._socket.connect(self._addr)

    def receive(self, use_lock: bool = False) -> dict:
        """
        Synchronously receives data from the server.

        Returns:
            (dict): raw data from the server.
        """
        try:
            if use_lock and self._lock:
                with self._lock:
                    buffer = self._socket.recv_multipart()
            else:
                buffer = self._socket.recv_multipart()

            msg = extract_reponse(buffer)
            return msg
        except Exception as exc:
            self._release_lock()
            self._logger.error(
                f"{self.__class__.__name__} failed to receive msg, got error of type: {exc}"
            )
            return {}


class AsyncZMQSubscriber(ZMQSubscriber):
    """An Async implementation of ZMQ subscriber"""

    _context = zmq.asyncio.Context()

    async def receive(self, use_lock: bool = False) -> dict:
        """
        Asynchrounsly receives data from the server.

        Returns:
            (dict): raw data from the server.
        """
        if use_lock:
            self._init_lock(asyncio_lock=True)
        try:
            if use_lock and self._lock:
                async with self._lock:
                    buffer = await self._socket.recv_multipart()
            else:
                buffer = await self._socket.recv_multipart()
            msg = extract_reponse(buffer)
            return msg
        except Exception as exc:
            self._release_lock()
            self._logger.error(
                f"{self.__class__.__name__} failed to receive msg, got error of type: {exc}"
            )
            return {}
