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
from abc import ABC, abstractmethod
import logging
import random
import zmq
import zmq.asyncio
from beartype import beartype

from movai_core_shared.envvars import MOVAI_ZMQ_TIMEOUT_MS, DEVICE_NAME
from movai_core_shared.exceptions import UnknownRequestError
from movai_core_shared.messages.general_data import Request
from movai_core_shared.core.zmq_base import ZMQBase


class ZMQServer(ZMQBase):
    """
    This class is a base class for any ZMQ server.
    """

    @beartype
    def __init__(
        self, server_name: str, bind_addr: str, new_loop: bool = False, debug: bool = False
    ) -> None:
        """Constructor"""
        random.seed()  # setting the seed for the random number generator
        identity = f"{DEVICE_NAME}_message_server_{random.getrandbits(24)}"
        super().__init__(identity, bind_addr, debug)
        self._name = server_name
        self._new_loop = new_loop

        self._initialized = False
        self._running = False
        self._ctx = None
        self._socket = None

    def _set_context(self) -> None:
        """Initializes the zmq context."""
        self._ctx = zmq.asyncio.Context()
        self._socket = self._ctx.socket(zmq.ROUTER)
        self._socket.setsockopt(zmq.IDENTITY, self._name.encode("ascii"))
        self._socket.setsockopt(zmq.SNDTIMEO, int(MOVAI_ZMQ_TIMEOUT_MS))
        if self._socket is None:
            raise zmq.ZMQError(msg="Failed to create socket")

    def _bind(self) -> None:
        """Binds the zmq socket to the appropriate file/address."""
        self._socket.bind(self._addr)
        self._logger.info(f"{self._name} is listening on {self._addr}")

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

    @abstractmethod
    async def handle(self, buffer: bytes) -> None:
        pass

    def close(self) -> None:
        """close the zmq socket."""
        if self._initialized:
            self._socket.close()
            self._ctx.destroy()
            self._socket = None
            self._ctx = None
            self._initialized = False

    def __del__(self):
        """closes the socket when the object is destroyed."""
        self.close()

    def init_server(self):
        """Initializes the server to listen on the specified address."""
        if self._initialized:
            self._logger.error(f"{self._name} is already initialized.")
            return

        try:
            self._set_context()
        except OSError:
            self._logger.error("failed to create server socket")
            return 1

        try:
            self._bind()
            self._initialized = True
        except OSError:
            self._logger.error(f"failed to bind socket on address {self._addr}")
            raise

    def run(self) -> int:
        """The main message dispatch loop.

        Returns:
            int: 1 in case of exception.
        """
        self.init_server()
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

    async def startup(self):
        """A funtion which is called once at server startup and can be used for initializing
        other tasks.
        """
        pass
