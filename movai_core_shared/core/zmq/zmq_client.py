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
import zmq
import zmq.asyncio

from movai_core_shared.core.zmq.zmq_base import ZMQBase
from movai_core_shared.core.zmq.zmq_helpers import create_msg, extract_reponse
from movai_core_shared.envvars import MOVAI_ZMQ_SEND_TIMEOUT_MS, MOVAI_ZMQ_RECV_TIMEOUT_MS


class ZMQClient(ZMQBase):
    """A very basic implementation of ZMQ Client"""

    def init_socket(self) -> None:
        """Initializes the socket and connect to the server."""
        self._init_lock()
        self.reset()

    def reset(self, force: bool = False) -> None:
        """Resets the socket without locking."""
        if self._socket and not self._socket.closed:
            if force:
                # Setting LINGER to 0 means that the socket will not wait at all
                # and will discard any unsent messages immediately
                self._socket.setsockopt(zmq.LINGER, 0)
                self._logger.info(f"{self.__class__.__name__} resetting the socket with force")
            self._socket.close()

        self._socket = self._context.socket(zmq.DEALER)
        self._socket.setsockopt(zmq.IDENTITY, self._identity)
        self._socket.setsockopt(zmq.RCVTIMEO, int(MOVAI_ZMQ_RECV_TIMEOUT_MS))
        self._socket.setsockopt(zmq.SNDTIMEO, int(MOVAI_ZMQ_SEND_TIMEOUT_MS))
        self._socket.connect(self._addr)

    def handle_socket_errors(self, exc: zmq.error.ZMQError, reset_socket=False) -> None:
        """Handles the socket errors."""
        if exc.errno == errno.ENOTSOCK:
            self._logger.warning(
                f"{self.__class__.__name__} socket error. "
                + f"Got exception: {exc} on ZMQ address {self._addr}. "
                + "Resetting the socket with potential data loss."
            )
            if reset_socket:
                self.reset(force=True)
        elif exc.errno == errno.EAGAIN:
            self._logger.warning(
                f"{self.__class__.__name__} socket error. "
                + f"Got exception: {exc} on ZMQ address {self._addr}. "
                + "Resetting the socket."
            )
            if reset_socket:
                self.reset()
        else:
            self._logger.error(
                f"{self.__class__.__name__} socket error. "
                + f"Got unhandled ZMQ exception: {exc} on ZMQ address {self._addr}"
            )

    def send(self, msg: dict, use_lock: bool = False) -> None:
        """
        Synchronously sends a message to the server.
        Args:
            data (dict): the msg representation
        """
        try:
            data = create_msg(msg)
            if use_lock and self._lock:
                with self._lock:
                    self._socket.send(data)
            else:
                self._socket.send(data)
        except Exception as exc:
            self._release_lock()
            self._logger.error(
                f"{self.__class__.__name__} failed to send message, got exception of type {exc}"
            )

    def receive(self, use_lock: bool = False) -> dict:
        """
        Synchronously receives data from the server.

        Returns:
            (dict): A response from the server.
        """
        try:
            if use_lock and self._lock:
                with self._lock:
                    buffer = self._socket.recv_multipart()
            else:
                buffer = self._socket.recv_multipart()
            response = extract_reponse(buffer)
            return response
        except zmq.error.ZMQError as exc:
            self.handle_socket_errors(exc)
            return {}
        except Exception as exc:
            self._release_lock()
            self._logger.error(
                f"{self.__class__.__name__} failed to receive data, got error of type: {exc}"
            )
            return {}


class AsyncZMQClient(ZMQClient):
    """An Async implementation of ZMQ Client"""

    _context = zmq.asyncio.Context()

    async def send(self, msg: dict, use_lock: bool = False) -> None:
        """
        Asynchrounously send the message to the server.

        Args:
            data (bytes): the msg representation
        """

        if use_lock:
            self._init_lock(asyncio_lock=True)
        try:
            data = create_msg(msg)
            if use_lock and self._lock:
                async with self._lock:
                    await self._socket.send(data)
            else:
                await self._socket.send(data)
        except asyncio.CancelledError:
            # This is a normal exception that is raised when the task is CancelledError
            self._socket.close()
        except TypeError as exc:
            self._logger.error(
                f"{self.__class__.__name__} failed to send message. "
                + f"Got type exception: {exc} on ZMQ address {self._addr}"
            )
        except ValueError as exc:
            self._logger.error(
                f"{self.__class__.__name__} failed to send message. "
                + f"Got value exception: {exc} on ZMQ address {self._addr}"
            )
        except zmq.error.ZMQError as exc:
            self.handle_socket_errors(exc)
        except Exception as exc:
            self._logger.error(
                f"{self.__class__.__name__} failed to send message. "
                + f"Got exception: {exc} on ZMQ address {self._addr}"
            )
        finally:
            self._release_lock()

    async def receive(self, use_lock: bool = False) -> dict:
        """
        Asynchrounsly receives data from the server.

        Returns:
            (dict): A response from the server.
        """
        response = {}
        if use_lock:
            self._init_lock()
        try:
            if use_lock and self._lock:
                async with self._lock:
                    buffer = await self._socket.recv_multipart()
            else:
                buffer = await self._socket.recv_multipart()
            response = extract_reponse(buffer)
        except asyncio.CancelledError:
            # This is a normal exception that is raised when the task is CancelledError
            self._socket.close()
        except zmq.error.ZMQError as exc:
            self.handle_socket_errors(exc)
        except Exception as exc:
            self._logger.error(
                f"{self.__class__.__name__} failed to receive data, got error of type: {exc}"
            )
        finally:
            self._release_lock()
        return response
