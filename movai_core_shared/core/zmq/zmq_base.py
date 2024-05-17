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
import zmq


class ZMQBase(ABC):
    """A base class for zmq components."""

    _context = zmq.Context()

    def __init__(self, identity: str, addr: str) -> None:
        """Initializes the object and the connection to the server.

        Args:
            identity (str): A unique identity which will be used by
                the server to identify the client.
            server_addr (str): The server addr and port in the form:
                'tcp://server_addr:port'
        """
        self._logger = getLogger(self.__class__.__name__)
        self._identity = identity.encode("utf-8")
        self._addr = addr
        self._lock = None
        self._socket = None
        self.init_socket()

    def __del__(self):
        """closes the socket when the object is destroyed."""
        # Close all sockets associated with this context and then terminate the context.
        if self._socket:
            self._socket.close()

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
        if self._lock and self._lock.locked():
            self._lock.release()

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
