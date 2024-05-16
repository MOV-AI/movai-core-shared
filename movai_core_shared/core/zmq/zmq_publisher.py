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
import zmq
import zmq.asyncio

from movai_core_shared.core.zmq.zmq_base import ZMQBase
from movai_core_shared.core.zmq.zmq_helpers import create_msg
from movai_core_shared.envvars import MOVAI_ZMQ_SEND_TIMEOUT_MS


class ZMQPublisher(ZMQBase):
    """A very basic implementation of ZMQ publisher"""

    def init_socket(self):
        """Creates the socket and sets a lock."""
        self._init_lock()
        self._socket = self._context.socket(zmq.PUB)
        self._socket.setsockopt(zmq.IDENTITY, self._identity)
        self._socket.setsockopt(zmq.SNDTIMEO, int(MOVAI_ZMQ_SEND_TIMEOUT_MS))
        self._socket.bind(self._addr)
        self._logger.info(f"{self.__class__.__name__} is bounded to: {self._addr}")

    def send(self, msg: dict, use_lock: bool = False) -> None:
        """
        Send the message request over ZeroMQ to the local robot message server.

        Args:
            msg (dict): The message request to be sent
        """
        try:
            data = create_msg(msg)
            if use_lock and self._lock:
                with self._lock:
                    self._socket.send(data)
            else:
                self._socket.send(data)
        except Exception as exc:
            self._logger.error(
                f"{self.__class__.__name__} failed to send message"
                + f"Got exception of type {exc} on ZMQ address {self._addr}"
            )
            self._release_lock()


class AsyncZMQPublisher(ZMQPublisher):
    """An Async implementation of ZMQ Publisher"""

    _context = zmq.asyncio.Context()

    async def send(self, msg: dict, use_lock: bool = False) -> None:
        """
        Send the message over ZeroMQ subscribers.

        Args:
            msg (dict): The message to be sent
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
        except zmq.error.ZMQError as exc:
            self.handle_socket_errors(exc)
        except Exception as exc:
            self._logger.error(
                f"{self.__class__.__name__} failed to send message"
                + f"Got exception of type {exc} on ZMQ address {self._addr}"
            )
        finally:
            self._release_lock()
