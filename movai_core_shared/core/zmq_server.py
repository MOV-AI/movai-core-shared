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
import sys
import json
from logging import Logger
import zmq
import zmq.asyncio


from movai_core_shared.exceptions import UnknownRequestError
from movai_core_shared.logger import Log

class ZMQServer:
    """
    This class is a base class for any ZMQ server.
    """
    def __init__(self, server_name: str, bind_addr: str, logger: Logger = None, debug: bool = False) -> None:
        """Constructor"""
        if not isinstance(server_name, str):
            raise ValueError("server name must be of type string.")
        if not isinstance(bind_addr, str):
            raise ValueError("bind address must be of type string.")
        if logger is None:
            logger = Log.get_logger(server_name)
        if not isinstance(logger, Logger):
            raise ValueError("logger must be of type logging.Logger.")
        if not isinstance(debug, bool):
            raise ValueError("debug must be of type bool.")
        self._name = server_name
        self._addr = bind_addr
        self._logger = logger
        self._debug = debug
        self._loop = asyncio.get_event_loop()
        self._running = False
        self._socket = None
        self._poller = None

    def init_server(self):
        """Initializes the server to listen on the specified address.
        """
        try:
            self._set_context()
        except OSError:  # aka any socket error
            self._logger.error("failed to create server socket")
            return 1

        # bind
        try:
            self._bind()
        except OSError as error:
            self._logger.error(f"failed to bind socket: {error}")
            self._close()
            return 1
        

    def run(self) -> int:
        """The main message dispatch loop.

        Returns:
            int: 1 in case of exception.
        """
        self._running = True        

        # flush stdout
        sys.stdout.flush()
        self._logger.info(f"{self.__class__.__name__} is running!!!")
        while self._running:
            # accept new request
            try:
                if self._debug:
                    self._logger.debug("Waiting for new requests.")
                self._loop.create_task(self._accept())
            except Exception as error:
                self._logger.error(error)
                continue

        # End while self._running
        self._close()

    async def _handle(self, msg_buffer, socket) -> None:
        # receive data
        index = len(msg_buffer) - 1
        buffer = msg_buffer[index]

        if buffer is None:
            self._logger.warning("Request has no buffer, can't handle request.")
            return

        request_msg = json.loads(buffer)
        # check for request in request
        if "request" not in request_msg:
            raise UnknownRequestError(f"The message format is unknown: {request_msg}.")

        request = request_msg.get("request")
        # validate request and and handler
        #self._validate_request(request)
        #self._validate_handler(request)
        # Handel the received request message
        response = await self._handle_request(request)
        # check if the client is expecting a response
        response_required = request.get("response_required")
        if response_required:
            await self._handle_response(socket, msg_buffer, response)

    def _set_context(self) -> None:
        """Initializes the zmq context."""
        context = zmq.asyncio.Context()
        self._socket = context.socket(zmq.ROUTER)

    def _bind(self) -> None:
        """Binds the zmq socket to the appropriate file/address."""
        self._socket.bind(self._addr)
        self._logger.info(f"{self.__class__.__name__} is listening on {self._addr}")

    async def _accept(self) -> None:
        """accepts new connections requests to zmq."""
        if self._socket is not None:
            
            request = await self._socket.recv_multipart()
            if self._debug:
                self._logger.debug("Accepting new request.")
                self._logger.debug(f"request:\n{request}")
            await asyncio.create_task(self._handle(request, self._socket))
        else:
            self._logger.warning("Cannot accept new requests, socket is not initialized.")

    def _close(self) -> None:
        """close the zmq socket."""
        self._socket.close()

    def _handle_response(self, socket, msg_buffer, response) -> None:
        """Send a response to the client.

        Args:
            socket: The socket allocated for communicating with the robot
            msg_buffer: The buffer for sending the response message
            response: The response message
        """
        if response.get("response") is None:
            response = {"response": response}
        # send the response back to the client
        index = len(msg_buffer) - 1
        msg_buffer[index] = json.dumps(response).encode("utf8")
        socket.send_multipart(msg_buffer)
        if self._debug:
            self._logger.debug(f"{self._name} successfully sent a respone.")

    async def _handle_request(self, request: dict):
        pass