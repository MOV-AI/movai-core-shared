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
import zmq
import zmq.asyncio

from movai_core_shared.core.zmq.zmq_base import ZMQBase
from movai_core_shared.core.zmq.zmq_helpers import extract_reponse


class ZMQSubscriber(ZMQBase):
    """A very basic implementation of ZMQ Subscriber"""

    def prepare_socket(self):
        """Creates the socket and set options."""
        self._socket: zmq.Socket = self._context.socket(zmq.SUB)
        self._socket.setsockopt(zmq.IDENTITY, self._identity)
        self.subscribe(b"", self._addr)

    def subscribe(self, topic: str, pub_addr:str):
        """Synchronously recieves data from the server.

        Returns:
            (bytes): raw data from the server.
        """
        if isinstance(topic, str):
            self._socket.setsockopt_string(zmq.SUBSCRIBE, topic)
        elif isinstance(topic, bytes):
            self._socket.setsockopt(zmq.SUBSCRIBE, b"")    
        self._socket.connect(pub_addr)
    
    def recieve(self):
        buffer = None
        try:
            buffer = self._socket.recv_multipart()
            response = extract_reponse(buffer)
            return response
        except Exception as exc:
            self._logger.error("error while trying to recieve data, %s", exc)
            return {}

class AsyncZMQSubscriber(ZMQSubscriber):
    """An Async implementation of ZMQ subscriber"""
    _context = zmq.asyncio.Context()

    def __init__(self, identity: str, bind_addr: str) -> None:
        super().__init__(identity, bind_addr)
        self._lock = asyncio.Lock()

    async def recieve(self):
        """Asynchrounsly recieves data from the server.

        Returns:
            (bytes): raw data from the server.
        """
        buffer = None
        try:
            buffer = await self._socket.recv_multipart()
            response = extract_reponse(buffer)
            return response
        except Exception as exc:
            self._logger.error("error while trying to recieve data, %s", exc)
        return buffer
