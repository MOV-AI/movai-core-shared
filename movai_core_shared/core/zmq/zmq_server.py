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
import logging
from abc import ABC, abstractmethod

import zmq
import zmq.asyncio
from beartype import beartype

from movai_core_shared.envvars import MOVAI_ZMQ_SEND_TIMEOUT_MS


class ZMQServer(ABC):
    """
    This class is a base class for any ZMQ server.
    """

    @beartype
    def __init__(
        self, server_name: str, bind_addr: str, debug: bool = False
    ) -> None:
        """Constructor"""
        self._name = server_name
        self._addr = bind_addr
        self._logger = logging.getLogger(server_name)
        self._debug = debug
        self._initialized = False
        self._running = False
        self._ctx = None
        self._socket = None
        self._parallel_tasks = []
        self.add_parallel_task(self._accept())

    def add_parallel_task(self, task) -> None:
        self._parallel_tasks.append(task)

    def _init_socket(self) -> None:
        """Initializes the zmq context."""
        try:
            self._ctx = zmq.asyncio.Context()
            self._socket = self._ctx.socket(zmq.ROUTER)
            self._socket.setsockopt(zmq.IDENTITY, self._name.encode("ascii"))
            self._socket.setsockopt(zmq.SNDTIMEO, int(MOVAI_ZMQ_SEND_TIMEOUT_MS))
            self._socket.bind(self._addr)
            self._logger.info(f"{self._name} is listening on {self._addr}")
        except OSError:
            self._logger.error(f"failed to bind socket on address {self._addr}")
            raise        

    async def _accept(self) -> None:
        """accepts new connections requests to zmq."""
#        await self.startup()
        while self._running:
            try:
                if self._debug:
                    self._logger.debug("Waiting for new requests.\n")
                buffer = await self._socket.recv_multipart()
                asyncio.create_task(self.handle(buffer))
                await asyncio.sleep(1)
            except Exception as error:
                self._logger.error(f"ZMQServer Error: {str(error)}")
                continue
        self.close()

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

        self._init_socket()
        self._initialized = True

    def start(self) -> bool:
        """The main message dispatch loop.

        Returns:
            int: 0 on success, 1 in case of exception.
        """
        try:
            self.init_server()
            if self._running:
                self._logger.warning("%s is already running", self._name)
                return True
            self._running = True
            if asyncio._get_running_loop() is None:
                asyncio.run(self.execute())
            else:
                asyncio.create_task(self._accept())
            self._logger.info("%s is running!!!", self._name)
            return True
        except Exception:
            self._logger.error("Failed to start %s", self._name)
            return False
        
    def stop(self):
        """Stops the server from running."""
        self._running = False

    async def execute(self) -> None:
        await asyncio.gather(*self._parallel_tasks)

    @abstractmethod
    async def handle(self, buffer: bytes) -> None:
        pass

    async def startup(self):
        """A funtion which is called once at server startup and can be used for initializing
        other tasks.
        """
        pass
