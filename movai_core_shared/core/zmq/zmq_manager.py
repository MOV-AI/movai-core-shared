from beartype import beartype
from enum import Enum
from logging import getLogger

from movai_core_shared.core.zmq.zmq_base import ZMQBase
from movai_core_shared.core.zmq.zmq_client import ZMQClient, AsyncZMQClient
from movai_core_shared.core.zmq.zmq_subscriber import ZMQSubscriber, AsyncZMQSubscriber
from movai_core_shared.core.zmq.zmq_publisher import ZMQPublisher, AsyncZMQPublisher
from movai_core_shared.core.zmq.zmq_helpers import generate_zmq_identity
from movai_core_shared.exceptions import ArgumentError

class ZMQType(Enum):
    client = 1
    AsyncClient = 2
    publisher = 3
    AsyncPublisher = 4
    Subscriber = 5
    AsyncSubscriber = 6

ZMQ_TYPES = {
    ZMQType.client:         {"type": ZMQClient,             "identity": "dealer"},
    ZMQType.AsyncClient:    {"type": AsyncZMQClient,        "identity": "dealer"},
    ZMQType.publisher:      {"type": ZMQPublisher,          "identity": "pub"},
    ZMQType.AsyncPublisher: {"type": AsyncZMQPublisher,     "identity": "pub"},
    ZMQType.Subscriber:     {"type": ZMQSubscriber,         "identity": "sub"},
    ZMQType.AsyncSubscriber: {"type": AsyncZMQSubscriber,    "identity": "sub"}
}

class ZMQManager:
    _logger = getLogger("ZMQManager")
    _clients = {
        ZMQType.client: {},
        ZMQType.AsyncClient: {},
        ZMQType.publisher: {},
        ZMQType.AsyncPublisher: {},
        ZMQType.Subscriber: {},
        ZMQType.AsyncSubscriber: {}
    }
    
    @classmethod
    def validate_server_addr(cls, server_addr: str):
        if not isinstance(server_addr, str):
            error_msg = "The argument server_addr must be of type string"
            cls._logger.error(error_msg)
            raise ArgumentError(error_msg)

    @classmethod
    @beartype
    def _get_or_create_zmq_object(cls, server_addr: str, zmq_type: ZMQType) -> ZMQBase:

        if zmq_type not in cls._clients:
            raise TypeError(f"{zmq_type} does not exist!")
        
        if server_addr in cls._clients[zmq_type]:
            return cls._clients[zmq_type][server_addr]
        else:
            identity = ZMQ_TYPES[zmq_type]["identity"]
            zmq_object = ZMQ_TYPES[zmq_type]["type"](identity, server_addr)
            cls._clients[zmq_type][server_addr] = zmq_object
            return zmq_object

    @classmethod
    def get_client(cls, server_addr: str, client_type: ZMQType) -> ZMQClient:
        client = cls._get_or_create_zmq_object(server_addr, client_type)
        return client
