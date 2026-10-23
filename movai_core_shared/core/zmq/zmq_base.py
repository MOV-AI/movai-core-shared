"""
   Copyright (C) Mov.ai  - All Rights Reserved
   Unauthorized copying of this file, via any medium is strictly prohibited
   Proprietary and confidential

   Usage:
        Basic 0MQ client for connecting 0MQ servers.

   Developers:
   - Erez Zomer (erez@mov.ai) - 2023
"""
import atexit
from abc import ABC, abstractmethod
from logging import getLogger
from typing import List, Optional
import threading
import weakref
import zmq

from movai_core_shared.envvars import MOVAI_ZMQ_SHUTDOWN_LINGER_MS

# how long the termination waits for a zmq object in use, e.g. sending a message
TERMINATE_LOCK_TIMEOUT_S = 0.1


class ZMQBase(ABC):
    """A base class for zmq components."""

    context = zmq.Context()
    # the context only terminates once the sockets of all the zmq objects using it are closed
    _instances: "weakref.WeakSet[ZMQBase]" = weakref.WeakSet()
    # a set can't be iterated while another thread adds to it
    _instances_lock = threading.Lock()
    # once set, the objects close their sockets when they finish their operations
    terminating = False

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
        with ZMQBase._instances_lock:
            ZMQBase._instances.add(self)
        self.init_socket()

    @classmethod
    def instances(cls) -> List["ZMQBase"]:
        """Returns the zmq objects alive which use the context of the class."""
        with ZMQBase._instances_lock:
            instances = list(ZMQBase._instances)
        return [instance for instance in instances if instance.context is cls.context]

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
            try:
                self._socket.setsockopt(zmq.LINGER, linger_ms)
            except zmq.error.ZMQError as exc:
                # e.g. closed meanwhile by the thread using it
                self._logger.debug("ZMQ %s failed to set the linger: %s", self._addr, exc)

    def _close_if_terminating(self) -> None:
        """Closes the socket if the context is terminating, it waits for its sockets to close."""
        if self.terminating:
            self.close()

    @classmethod
    def terminate(cls, linger_ms: int = MOVAI_ZMQ_SHUTDOWN_LINGER_MS) -> None:
        """Sends the messages still queued on the synchronous zmq objects, then closes them.

        Blocks until all the queued messages are sent or `linger_ms` elapses.
        Called automatically when the interpreter exits.

        Args:
            linger_ms (int): How long to wait for the queued messages to be sent.
        """
        if ZMQBase.context.closed:
            return
        zmq_objects = ZMQBase.instances()
        # the linger can't be changed once the termination started
        for zmq_object in zmq_objects:
            zmq_object.set_linger(linger_ms)
        ZMQBase.terminating = True
        locks = []
        try:
            for zmq_object in zmq_objects:
                # also the linger of a socket replaced meanwhile, e.g. by a reset
                if zmq_object.lock is None:
                    zmq_object.close(linger_ms)
                elif zmq_object.lock.acquire(timeout=TERMINATE_LOCK_TIMEOUT_S):
                    locks.append(zmq_object.lock)
                    zmq_object.close(linger_ms)
                # else busy, e.g. waiting for a message, and closing its socket from another
                # thread isn't safe: it closes it itself once its operation finishes,
                # successfully or interrupted by the termination
            # waits for the sockets to be closed and to send their queued messages
            ZMQBase.context.term()
        finally:
            for lock in locks:
                lock.release()

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


# pyzmq doesn't terminate the context when the interpreter exits,
# so the messages still queued (sent right before exiting) would be lost
atexit.register(ZMQBase.terminate)
