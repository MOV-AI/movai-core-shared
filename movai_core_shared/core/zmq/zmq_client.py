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
import errno
import threading
import time
import uuid
from typing import Dict, Optional

import zmq
import zmq.asyncio

from movai_core_shared.core.zmq.zmq_base import ZMQBase
from movai_core_shared.exceptions import MessageError
from movai_core_shared.core.zmq.zmq_helpers import create_msg, extract_response
from movai_core_shared.envvars import (
    MOVAI_ZMQ_SEND_TIMEOUT_MS,
    MOVAI_ZMQ_RECV_TIMEOUT_MS,
    MOVAI_ZMQ_SHUTDOWN_LINGER_MS,
)


def _new_request_id() -> bytes:
    """
    Generates the id frame which is sent ahead of a request
    so the client can match responses to requests.
    """
    return uuid.uuid4().hex.encode("utf-8")


class ZMQClient(ZMQBase):
    """A very basic implementation of ZMQ Client"""

    zmq_socket_type = zmq.DEALER

    def init_lock(self) -> None:
        """Initializes the lock."""
        self.lock = threading.Lock()

    def init_socket(self) -> None:
        """Initializes the socket and connect to the server."""
        self.init_lock()
        self.reset()

    def reset(self, force: bool = False, use_lock: bool = False) -> None:
        """Resets the socket and reconnects to the server."""
        if use_lock and self.lock:
            with self.lock:
                self._reset(force)
        else:
            self._reset(force)

    def _reset(self, force: bool = False) -> None:
        """Resets the socket and reconnects to the server."""
        if self._socket and not self._socket.closed:
            if force:
                # Setting LINGER to 0 means that the socket will not wait at all
                # and will discard any unsent messages immediately
                self._socket.setsockopt(zmq.LINGER, 0)
                self._logger.info("ZMQ resetting %s with force", self._addr)
            self._socket.close()
            time.sleep(0.1)

        if self._socket is not None:
            # The server ignores the new connection while the old one,
            # with the same identity, isn't closed yet
            # the old socket may still be sending its messages
            self._identity = f"{self._base_identity}_{uuid.uuid4().hex}".encode("utf-8")

        self._socket: zmq.Socket = self.context.socket(self.zmq_socket_type)
        self._socket.setsockopt(zmq.IDENTITY, self._identity)
        # the default linger is infinite: once closed, a socket that can't deliver
        # its messages would block the context termination at exit forever
        self._socket.setsockopt(zmq.LINGER, MOVAI_ZMQ_SHUTDOWN_LINGER_MS)
        if self.zmq_socket_type in [zmq.DEALER]:
            self._logger.info("ZMQ connecting DEALER to: %s", self._addr)
            self._socket.setsockopt(zmq.RCVTIMEO, int(MOVAI_ZMQ_RECV_TIMEOUT_MS))
            self._socket.setsockopt(zmq.SNDTIMEO, int(MOVAI_ZMQ_SEND_TIMEOUT_MS))
            self._socket.connect(self._addr)
        elif self.zmq_socket_type in [zmq.SUB]:
            self._logger.info("ZMQ connecting SUBSCRIBER to: %s", self._addr)
            self._socket.setsockopt_string(zmq.SUBSCRIBE, "")
            self._socket.connect(self._addr)
        elif self.zmq_socket_type in [zmq.ROUTER, zmq.PUB]:
            self._logger.info("ZMQ connecting ROUTER/PUBLISHER to: %s", self._addr)
            self._socket.setsockopt(zmq.SNDTIMEO, int(MOVAI_ZMQ_SEND_TIMEOUT_MS))
            self._socket.bind(self._addr)
            self._logger.info("%s is bounded to: %s", self.__class__.__name__, self._addr)
        else:
            self._logger.critical("ZMQ %s has an unsupported socket type.", self._addr)

    def handle_socket_errors(self, exc: zmq.error.ZMQError, reset_socket=True) -> None:
        """Handles the socket errors
        Args:
            exc (zmq.error.ZMQError): the exception
            reset_socket (bool): whether to reset the socket
        Returns:
            None
        Raises:
            exc: the exception
        """
        if exc.errno == errno.ENOTSOCK:
            self._logger.warning("ZMQ socket error: %s got exception: %s.", self._addr, exc)
            if reset_socket:
                self._logger.warning("Resetting ZMQ %s with potential data loss.", self._addr)
                self.reset(force=True)
        elif exc.errno == errno.EAGAIN:
            self._logger.warning("ZMQ socket error: %s got exception: %s.", self._addr, exc)
            if reset_socket:
                self._logger.warning("Resetting ZMQ %s.", self._addr)
                self.reset()
        else:
            self._logger.error(
                "ZMQ socket error: %s got unhandled ZMQ exception: %s ", self._addr, exc
            )

    def send(self, msg: dict, use_lock: bool = False) -> None:
        """
        Synchronously sends a message to the server.
        Args:
            data (dict): the msg representation
            use_lock (bool): whether to use the lock
        Returns:
            None
        """
        try:
            data = create_msg(msg)
            if use_lock and self.lock:
                with self.lock:
                    self._socket.send(data)
            else:
                self._socket.send(data)
        except Exception as exc:
            self._logger.error("ZMQ failed to send message, got exception of type %s", exc)
            raise exc

    def receive(self, use_lock: bool = False) -> dict:
        """
        Synchronously receives data from the server.
        Args:
            use_lock (bool): whether to use the lock
        Returns:
            (dict): A response from the server.
        """
        response = {}
        try:
            if use_lock and self.lock:
                with self.lock:
                    buffer = self._socket.recv_multipart()
            else:
                buffer = self._socket.recv_multipart()
            if not buffer:
                self._logger.debug("ZMQ received empty buffer from %s", self._addr)
                return response
            response = extract_response(buffer)
            return response
        except zmq.error.ZMQError as exc:
            self.handle_socket_errors(exc)
        except Exception as exc:
            self._logger.error("ZMQ failed to receive data, got error of type: %s", exc)
            raise exc
        return response

    def request(self, msg: dict) -> dict:
        """
        Synchronously sends a request and waits for its response.

        The send and the receive are done under the same lock, so concurrent
        threads can't take each other's responses. The request id frame
        makes sure that a late response to an earlier (timed out) request is
        discarded instead of being returned.

        Args:
            msg (dict): The request to send.
        Returns:
            (dict): The response from the server, an empty dict on timeout.
        Raises:
            MessageError: If sending the request or receiving the response fails.
        """
        data = create_msg(msg)
        req_id = _new_request_id()
        with self.lock:
            try:
                self._socket.send_multipart([req_id, data])
                while True:
                    buffer = self._socket.recv_multipart()
                    if buffer[0] == req_id:
                        return extract_response(buffer)
                    self._logger.debug("ZMQ discarding expired response from %s", self._addr)
            except zmq.error.ZMQError as exc:
                self.handle_socket_errors(exc)
            except Exception as exc:
                self._logger.error("ZMQ failed to receive response, got error of type: %s", exc)
                raise MessageError("Failed to receive response from the server: " + str(exc))
        return {}


class AsyncZMQClient(ZMQClient):
    """An Async implementation of ZMQ Client"""

    _socket: zmq.asyncio.Socket
    context = zmq.asyncio.Context()

    def __init__(self, identity: str, addr: str) -> None:
        # requests waiting for a response, by request id
        self._pending: Dict[bytes, asyncio.Future] = {}
        # task routing the responses to the pending requests
        self._reader: Optional[asyncio.Task] = None
        super().__init__(identity, addr)

    def init_lock(self) -> None:
        """Initializes the lock the async way."""
        if self.lock is None:
            try:
                asyncio.get_running_loop()
                self.lock = asyncio.Lock()
            except RuntimeError:
                pass

    async def send(self, msg: dict, use_lock: bool = False) -> None:
        """
        Asynchrounously send the message to the server.

        Args:
            msg (dict): The message to send.
            use_lock (bool): Whether to use the lock.
        Returns:
            None
        """
        try:
            data = create_msg(msg)
            if use_lock and self.lock:
                async with self.lock:
                    await self._socket.send(data)
            else:
                await self._socket.send(data)
        except asyncio.CancelledError as exc:
            # This is a normal exception that is raised when the task is cancelled
            self._socket.close()
            raise exc
        except zmq.error.ZMQError as exc:
            self.handle_socket_errors(exc)
        except Exception as exc:
            self._logger.error(
                f"{self.__class__.__name__} failed to send message. "
                + f"{self._addr} got exception: {exc} "
            )
            raise exc

    async def receive(self, use_lock: bool = False) -> dict:
        """
        Asyncronously receives data from the server.

        Args:
            use_lock (bool): Whether to use the lock.
        Returns:
            (dict): A response from the server.
            In case of an error, an empty dict is returned.
        """
        response = {}
        if use_lock:
            self.init_lock()
        try:
            if use_lock and self.lock:
                async with self.lock:
                    buffer = await self._socket.recv_multipart()
            else:
                buffer = await self._socket.recv_multipart()
            response = extract_response(buffer)
        except asyncio.CancelledError as exc:
            # This is a normal exception that is raised when the task is cancelled
            self._socket.close()
            raise exc
        except zmq.error.ZMQError as exc:
            self.handle_socket_errors(exc)
        except Exception as exc:
            self._logger.error("ZMQ failed to receive data, got error of type: %s", exc)
            raise exc
        return response

    async def request(self, msg: dict) -> dict:
        """
        Asynchronously sends a request and waits for its response.

        Several coroutines can have requests in flight on the socket at the
        same time, each one gets the response with its own request id frame.

        Args:
            msg (dict): The request to send.
        Returns:
            (dict): The response from the server, an empty dict on timeout.
        Raises:
            MessageError: If sending the request fails.
        """
        data = create_msg(msg)
        req_id = _new_request_id()
        loop = asyncio.get_running_loop()
        future = loop.create_future()
        self._pending[req_id] = future
        try:
            self._start_reader(loop)
            await self._socket.send_multipart([req_id, data])
            return await asyncio.wait_for(future, MOVAI_ZMQ_RECV_TIMEOUT_MS / 1000)
        except asyncio.TimeoutError:
            # no need to reset the socket, a late response will be discarded by its id
            self._logger.warning("ZMQ timed out waiting for a response from %s", self._addr)
        except zmq.error.ZMQError as exc:
            self.handle_socket_errors(exc)
        except Exception as exc:
            self._logger.error(
                "ZMQ failed to send request to %s, got error of type: %s", self._addr, exc
            )
            raise MessageError("Failed to send request to the server.")
        finally:
            self._pending.pop(req_id, None)
            if not self._pending and self._reader is not None and self._reader.get_loop() is loop:
                # nothing left to wait for, don't leave a receive pending on the socket
                self._reader.cancel()
                self._reader = None
        return {}

    def _start_reader(self, loop: asyncio.AbstractEventLoop) -> None:
        """Starts the task which routes the responses, if it is not running."""
        if self._reader is None or self._reader.done() or self._reader.get_loop() is not loop:
            self._reader = loop.create_task(self._read_responses())

    async def _read_responses(self) -> None:
        """Receives the responses and hands each one to the request waiting for it."""
        while self._pending:
            sock = self._socket
            try:
                buffer = await sock.recv_multipart()
            except zmq.error.Again:
                # RCVTIMEO elapsed, keep receiving while there are pending requests
                continue
            except (asyncio.CancelledError, zmq.error.ZMQError) as exc:
                if sock.closed and sock is not self._socket:
                    # the socket was reset (closing it cancels the receive), use the new one
                    continue
                if isinstance(exc, asyncio.CancelledError):
                    raise
                self._logger.error("ZMQ failed to receive from %s: %s", self._addr, exc)
                return

            future = self._pending.get(buffer[0])
            if future is None or future.done():
                self._logger.debug("ZMQ discarding expired response from %s", self._addr)
                continue
            future.set_result(extract_response(buffer))
