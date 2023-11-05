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
        pass
