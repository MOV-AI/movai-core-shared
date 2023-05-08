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

from movai_core_shared.logger import Log

class ZMQServer:
    """
    This class is a base class for any ZMQ server.
    """
    def __init__(self) -> None:
        """Constructor"""
        self._role = None
        self._logger = Log.get_logger(self.__class__.__name__)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        self._running = False
        self._socket = None
        self._poller = None

    def run(self) -> int:
        """The main message dispatch loop.

        Returns:
            int: 1 in case of exception.
        """
        self._running = True

        # create socket
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

        # flush stdout
        sys.stdout.flush()
        self._logger.debug(f"{self.__class__.__name__} is running!!!")
        while self._running:
            # accept new request
            try:
                self._accept()
            except Exception as error:
                self._logger.error(error)
                continue

        # End while self._running
        self._close()

    def _handle(self, msg_buffer, socket) -> None:
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
        self._validate_request(request)
        self._validate_handler(request)
        # Handel the received request message
        response = self._handle_request(request)
        # check if the client is expecting a response
        response_required = request.get("response_required")
        if response_required:
            self._handle_response(socket, msg_buffer, response)

    def _set_context(self) -> None:
        """Initializes the zmq context."""
        context = zmq.Context()
        self._socket = context.socket(zmq.ROUTER)

    def _bind(self) -> None:
        """Binds the zmq socket to the appropriate file/address."""
        self._logger.debug(f"Going to listen on {MESSAGE_SERVER_BIND_ADDR}")
        self._socket.bind(MESSAGE_SERVER_BIND_ADDR)

    def _accept(self) -> None:
        """accepts new connections requests to zmq."""
        if self._socket is not None:
            self._logger.debug("Waiting for new requests.")
            request = self._socket.recv_multipart()
            self._logger.debug("Accepting new request.")
            self._logger.debug(f"request:\n{request}")
            _thread.start_new_thread(self._handle, (request, self._socket))
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
        self._logger.debug(f"{self.__class__.__name__} successfully sent a respone.")

    def _handler_request(self, request):
        pass