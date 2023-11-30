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
import threading
import zmq
import zmq.asyncio

from movai_core_shared.core.zmq.zmq_base import ZMQBase
from movai_core_shared.core.zmq.zmq_helpers import create_msg, extract_reponse
from movai_core_shared.envvars import MOVAI_ZMQ_SEND_TIMEOUT_MS, MOVAI_ZMQ_RECV_TIMEOUT_MS


class ZMQClient(ZMQBase):
    """A very basic implementation of ZMQ Client"""

    def _init_lock(self) -> None:
        """Initializes the lock."""
        self._lock = threading.Lock()

    def init_socket(self) -> None:
        """Initializes the socket and connect to the server."""
        self._init_lock()
        self._socket = self._context.socket(zmq.DEALER)
        self._socket.setsockopt(zmq.IDENTITY, self._identity)
        self._socket.setsockopt(zmq.RCVTIMEO, int(MOVAI_ZMQ_RECV_TIMEOUT_MS))
        self._socket.setsockopt(zmq.SNDTIMEO, int(MOVAI_ZMQ_SEND_TIMEOUT_MS))
        self._socket.connect(self._addr)

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
            if self._lock and self._lock.locked():
                self._lock.release()
            self._logger.error(
                f"{self.__class__.__name__} failed to send message, got exception of type {exc}"
            )

    def recieve(self, use_lock: bool = False) -> dict:
        """
        Synchronously recieves data from the server.

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
        except Exception as exc:
            if self._lock and self._lock.locked():
                self._lock.release()
            self._logger.error(
                f"{self.__class__.__name__} failed to recieve data, got error of type: {exc}"
            )
            return {}


class AsyncZMQClient(ZMQClient):
    """An Async implementation of ZMQ Client"""
    _context = zmq.asyncio.Context()

    def _init_lock(self) -> None:
        """Initializes the lock."""
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
            data (bytes): the msg representation
        """
        if use_lock:
            self._init_lock()
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
        except Exception as exc:
            self._logger.error(
                f"{self.__class__.__name__} failed to send message, got exception of type {exc}"
            )
        finally:
            if self._lock and self._lock.locked():
                self._lock.release()

    async def recieve(self, use_lock: bool = False) -> dict:
        """
        Asynchrounsly recieves data from the server.

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
        except Exception as exc:
            self._logger.error(
                f"{self.__class__.__name__} failed to recieve data, got error of type: {exc}"
            )
        finally:
            if self._lock and self._lock.locked():
                self._lock.release()
        return response
