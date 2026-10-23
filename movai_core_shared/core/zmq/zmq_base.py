"""
   Copyright (C) Mov.ai  - All Rights Reserved
   Unauthorized copying of this file, via any medium is strictly prohibited
   Proprietary and confidential

   Usage:
        Basic 0MQ client for connecting 0MQ servers.

   Developers:
   - Erez Zomer (erez@mov.ai) - 2023
"""
from abc import ABC, abstractmethod
from logging import getLogger
from typing import List, Optional
import weakref
import zmq


class ZMQBase(ABC):
    """A base class for zmq components."""

    context = zmq.Context()
    # the context only terminates once the sockets of all the zmq objects using it are closed
    _instances: "weakref.WeakSet[ZMQBase]" = weakref.WeakSet()

    def __init__(self, identity: str, addr: str) -> None:
        """Initializes the object and the connection to the server.

        Args:
            identity (str): A unique identity which will be used by
                the server to identify the client.
            server_addr (str): The server addr and port in the form:
                'tcp://server_addr:port'
        """
        self._logger = getLogger(self.__class__.__name__)
        self._base_identity = identity
        self._identity = identity.encode("utf-8")
        self._addr = addr
        self.lock = None
        self._socket = None
        ZMQBase._instances.add(self)
        self.init_socket()

    @classmethod
    def instances(cls) -> List["ZMQBase"]:
        """Returns the zmq objects alive which use the context of the class."""
        return [
            instance for instance in list(ZMQBase._instances) if instance.context is cls.context
        ]

    def __del__(self):
        """closes the socket when the object is destroyed."""
        # Close all sockets associated with this context and then terminate the context.
        if self._socket:
            self._socket.close()

    def close(self, linger_ms: Optional[int] = None) -> None:
        """Closes the socket.

        Args:
            linger_ms (int): How long to keep sending the queued messages,
                by default the linger of the socket.
        """
        if self._socket and not self._socket.closed:
            self._socket.close(linger=linger_ms)

    def set_linger(self, linger_ms: int) -> None:
        """Sets how long the socket keeps sending the queued messages once closed.

        Unlike other options, the linger can be set while another thread uses the socket:
        libzmq stores it atomically, the context termination reads it from another thread.
        Once the context termination started, it can't be changed anymore.

        Args:
            linger_ms (int): How long to keep sending the queued messages.
        """
        if self._socket and not self._socket.closed:
            self._socket.setsockopt(zmq.LINGER, linger_ms)

    @abstractmethod
    def init_socket(self):
        """
        An abstract medthod which allows every ZMQ component to initiliaze the socket by
        it's own needs.
        """

    @abstractmethod
    def init_lock(self):
        """
        An abstract method which allows every ZMQ component to initiliaze the lock by
        it's own needs.
        """

    def release_lock(self) -> None:
        """
        An abstract method which allows every ZMQ component to release the lock by
        it's own needs.
        """
        if self.lock and self.lock.locked():
            self.lock.release()

    @abstractmethod
    def handle_socket_errors(self, exc):
        """
        An abstract method which allows every ZMQ component to handle the error by
        it's own needs.
        """

    @abstractmethod
    def receive(self, use_lock: bool = False):
        """
        An abstract method which allows every ZMQ component to receive the message by
        it's own needs.
        """

    @abstractmethod
    def send(self, msg: dict, use_lock: bool = False):
        """
        An abstract method which allows every ZMQ component to send the message by
        it's own needs.
        """

    def recieve(self, use_lock: bool = False):
        """
        Function for retrocompatibility which call recieve() member function
        """
        if self.receive is None:
            raise NotImplementedError("receive() method is not implemented")
        return self.receive(use_lock=use_lock)
