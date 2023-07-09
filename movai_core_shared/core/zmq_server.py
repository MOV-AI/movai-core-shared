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
import json
import logging
from abc import ABC, abstractmethod
from threading import Lock

import zmq
import zmq.asyncio
from beartype import beartype

from movai_core_shared.exceptions import UnknownRequestError
from movai_core_shared.messages.general_data import Request


class ZMQServer(ABC):
    """
    This class is a base class for any ZMQ server.
    """

    _initialized = {}

    @beartype
    def __init__(
        self, server_name: str, bind_addr: str, new_loop: bool = False, debug: bool = False
    ) -> None:
        """Constructor"""
        self._name = server_name
        self._addr = bind_addr
        self._logger = logging.getLogger(server_name)
        self._new_loop = new_loop
        self._debug = debug
        self._initialized = False
        self._running = False
        self._ctx = None
        self._socket = None
        self._lock = Lock()

    def _set_context(self) -> None:
        """Initializes the zmq context."""
        self._ctx = zmq.asyncio.Context()
        self._socket = self._ctx.socket(zmq.ROUTER)
        if self._socket is None:
            raise zmq.ZMQError(msg="Failed to create socket")

    def _bind(self) -> None:
        """Binds the zmq socket to the appropriate file/address."""
        self._socket.bind(self._addr)
        self._logger.info(f"{self.__class__.__name__} is listening on {self._addr}")

    async def _accept(self) -> None:
        """accepts new connections requests to zmq."""
        while self._running:
            try:
                if self._debug:
                    self._logger.debug("Waiting for new requests.\n")
                with self._lock:
                    request = await self._socket.recv_multipart()
                asyncio.create_task(self._handle(request))
            except Exception as error:
                self._logger.error(f"ZMQServer Error: {str(error)}")
                continue
        self.close()

    async def _handle(self, msg_buffer) -> None:
        index = len(msg_buffer) - 1
        buffer = msg_buffer[index]

        if buffer is None:
            self._logger.warning("Request has no buffer, can't handle request.")
            return

        request_msg = json.loads(buffer)
        if "request" not in request_msg:
            raise UnknownRequestError(f"The message format is unknown: {request_msg}.")
        request = request_msg.get("request")

        if self._debug:
            general_request = Request(**request)
            self._logger.debug(str(general_request))

        response = await self.handle_request(request)
        response_required = request.get("response_required")
        if response_required:
            if response.get("response") is None:
                response = {"response": response}
            await self.handle_response(response)
            index = len(msg_buffer) - 1
            msg_buffer[index] = json.dumps(response).encode("utf8")
            with self._lock:
                self._socket.send_multipart(msg_buffer)
            if self._debug:
                self._logger.debug(f"{self._name} successfully sent a respone.")

    def close(self) -> None:
        """close the zmq socket."""
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

    async def handle_response(self, response: dict) -> dict:
        """Handles the response before it is sent back to the client.

        Args:
            response: The response dict.
        """
        pass

    @abstractmethod
    async def handle_request(self, request: dict) -> dict:
        """Handles the request recieved by the server.

        Args:
            request(dict): The request recieved.
        """
