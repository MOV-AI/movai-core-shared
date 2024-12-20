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
import zmq
import zmq.asyncio

from movai_core_shared.core.zmq.zmq_base import ZMQBase
from movai_core_shared.core.zmq.zmq_helpers import create_msg, extract_reponse
from movai_core_shared.envvars import MOVAI_ZMQ_SEND_TIMEOUT_MS, MOVAI_ZMQ_RECV_TIMEOUT_MS


class ZMQClient(ZMQBase):
    """A very basic implementation of ZMQ Client"""

    zmq_socket_type = zmq.DEALER

    def init_lock(self) -> None:
        """Initializes the lock."""
        self._lock = threading.Lock()

    def init_socket(self) -> None:
        """Initializes the socket and connect to the server."""
        self.init_lock()
        self.reset()

    def reset(self, force: bool = False, use_lock: bool = False) -> None:
        """Resets the socket and reconnects to the server."""
        if use_lock and self._lock:
            with self._lock:
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

        self._socket: zmq.Socket = self._context.socket(self.zmq_socket_type)
        self._socket.setsockopt(zmq.IDENTITY, self._identity)
        if self.zmq_socket_type in [zmq.DEALER]:
            self._logger.info(f"ZMQ connecting DEALER to: {self._addr}")
            self._socket.setsockopt(zmq.RCVTIMEO, int(MOVAI_ZMQ_RECV_TIMEOUT_MS))
            self._socket.setsockopt(zmq.SNDTIMEO, int(MOVAI_ZMQ_SEND_TIMEOUT_MS))
            self._socket.connect(self._addr)
        elif self.zmq_socket_type in [zmq.SUB]:
            self._logger.info(f"ZMQ connecting SUBSCRIBER to: {self._addr}")
            self._socket.setsockopt_string(zmq.SUBSCRIBE, "")
            self._socket.connect(self._addr)
        elif self.zmq_socket_type in [zmq.ROUTER, zmq.PUB]:
            self._logger.info(f"ZMQ connecting ROUTER/PUBLISHER to: {self._addr}")
            self._socket.setsockopt(zmq.SNDTIMEO, int(MOVAI_ZMQ_SEND_TIMEOUT_MS))
            self._socket.bind(self._addr)
            self._logger.info(f"{self.__class__.__name__} is bounded to: {self._addr}")
        else:
            self._logger.critical(f"ZMQ {self._addr} has an unsupported socket type.")

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
            self._logger.warning(f"ZMQ socket error: {self._addr} got exception: {exc}.")
            if reset_socket:
                self._logger.warning(f"Resetting ZMQ {self._addr} with potential data loss.")
                self.reset(force=True)
        elif exc.errno == errno.EAGAIN:
            self._logger.warning(f"ZMQ socket error: {self._addr} got exception: {exc}.")
            if reset_socket:
                self._logger.warning(f"Resetting ZMQ {self._addr}.")
                self.reset()
        else:
            self._logger.error(
                f"ZMQ socket error: {self._addr} got unhandled ZMQ exception: {exc} "
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
            if use_lock and self._lock:
                with self._lock:
                    self._socket.send(data)
            else:
                self._socket.send(data)
        except Exception as exc:
            self._logger.error(f"ZMQ failed to send message, got exception of type {exc}")
            raise exc
        finally:
            if use_lock and self._lock.locked():
                self._lock.release()

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
            if use_lock and self._lock:
                with self._lock:
                    buffer = self._socket.recv_multipart()
            else:
                buffer = self._socket.recv_multipart()
            if not buffer:
                self._logger.debug(f"ZMQ received empty buffer from {self._addr}")
                return response
            response = extract_reponse(buffer)
            return response
        except zmq.error.ZMQError as exc:
            self.handle_socket_errors(exc)
        except Exception as exc:
            self._logger.error(f"ZMQ failed to receive data, got error of type: {exc}")
            raise exc
        finally:
            if use_lock and self._lock.locked():
                self._lock.release()
        return response


class AsyncZMQClient(ZMQClient):
    """An Async implementation of ZMQ Client"""

    _socket: zmq.asyncio.Socket
    _context = zmq.asyncio.Context()

    def init_lock(self) -> None:
        """Initializes the lock the async way."""
        if self._lock is None:
            try:
                asyncio.get_running_loop()
                self._lock = asyncio.Lock()
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
            if use_lock and self._lock:
                async with self._lock:
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
        finally:
            if use_lock:
                self.release_lock()

    async def receive(self, use_lock: bool = False) -> dict:
        """
        Asyncronously receives data from the server.

        Args:
            (dict): A response from the server.
            use_lock (bool): Whether to use the lock.
        Returns:
            (dict): A response from the server.
            In case of an error, an empty dict is returned.
        """
        response = {}
        if use_lock:
            self.init_lock()
        try:
            if use_lock and self._lock:
                async with self._lock:
                    buffer = await self._socket.recv_multipart()
            else:
                buffer = await self._socket.recv_multipart()
            response = extract_reponse(buffer)
        except asyncio.CancelledError as exc:
            # This is a normal exception that is raised when the task is cancelled
            self._socket.close()
            raise exc
        except zmq.error.ZMQError as exc:
            self.handle_socket_errors(exc)
        except Exception as exc:
            self._logger.error(f"ZMQ failed to receive data, got error of type: {exc}")
            raise exc
        finally:
            if use_lock:
                self.release_lock()
        return response
