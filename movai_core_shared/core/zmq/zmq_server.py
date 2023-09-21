"""
   Copyright (C) Mov.ai  - All Rights Reserved
   Unauthorized copying of this file, via any medium is strictly prohibited
   Proprietary and confidential

   Usage:
        Basic 0MQ client for connecting 0MQ servers.

   Developers:
   - Erez Zomer (erez@mov.ai) - 2023
"""
import asyncio
from abc import abstractmethod
import threading

import zmq
import zmq.asyncio
from beartype import beartype

from movai_core_shared.envvars import MOVAI_ZMQ_SEND_TIMEOUT_MS
from movai_core_shared.core.zmq.zmq_base import ZMQBase

class ZMQServer(ZMQBase):
    """
    This class is a base class for any ZMQ server.
    """
    _context = zmq.asyncio.Context()

    @beartype
    def __init__(
        self, server_name: str, bind_addr: str, new_loop: bool = False, debug: bool = False
    ) -> None:
        """Constructor"""
        super().__init__(server_name, bind_addr)
        self._name = server_name
        self._new_loop = new_loop
        self._debug = debug
        self._initialized = False
        self._running = False
        self._lock = threading.Lock()

    def prepare_socket(self) -> None:
        """Initializes the zmq context."""
        self._socket = self._context.socket(zmq.ROUTER)
        self._socket.setsockopt(zmq.IDENTITY, self._identity)
        self._socket.setsockopt(zmq.SNDTIMEO, int(MOVAI_ZMQ_SEND_TIMEOUT_MS))
        self._bind()

    def _bind(self) -> None:
        """Binds the zmq socket to the appropriate file/address."""
        try:
            self._socket.bind(self._addr)
            self._logger.info(f"{self._name} is listening on {self._addr}")
        except OSError:
            self._logger.error("%s failed to bind socket on address: %s", self._name, self._addr)
            raise


    def _accept(self) -> None:
        """accepts new connections requests to zmq."""
        self.startup()
        while self._running:
            try:
                if self._debug:
                    self._logger.debug("Waiting for new requests.\n")
                buffer = self._socket.recv_multipart()
                self.handle(buffer)
            except Exception as error:
                self._logger.error(f"ZMQServer Error: {str(error)}")
                continue
        self.close()

    def close(self) -> None:
        """close the zmq socket."""
        if self._initialized:
            self._socket.close()
            self._socket = None
            self._initialized = False

    def __del__(self):
        """closes the socket when the object is destroyed."""
        self.close()

    def start(self) -> int:
        """The main message dispatch loop.

        Returns:
            int: 1 in case of exception.
        """
        if self._running:
            self._logger.warning(f"{self._name} is already ruuning")
            return
        self._running = True
        self._logger.info(f"{self.__class__.__name__} is running!!!")
        if self._new_loop:
            asyncio.run(self._accept())
        else:
            asyncio.create_task(self._accept())

    def stop(self):
        """Stops the server from running."""
        self._running = False

    @abstractmethod
    def handle(self, buffer: bytes) -> None:
        pass

    def startup(self):
        """A funtion which is called once at server startup and can be used for initializing
        other tasks.
        """
        pass


class AsyncZMQServer(ZMQServer):
    
    
    async def _accept(self) -> None:
        """accepts new connections requests to zmq."""
        await self.startup()
        while self._running:
            try:
                if self._debug:
                    self._logger.debug("Waiting for new requests.\n")
                buffer = await self._socket.recv_multipart()
                asyncio.create_task(self.handle(buffer))
            except Exception as error:
                self._logger.error(f"ZMQServer Error: {str(error)}")
                continue
        self.close()
    
    async def handle(self, buffer: bytes) -> None:
        pass

    async def startup(self):
        """A funtion which is called once at server startup and can be used for initializing
        other tasks.
        """
        pass