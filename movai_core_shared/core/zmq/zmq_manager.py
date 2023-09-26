from logging import getLogger

from movai_core_shared.core.zmq.zmq_base import ZMQBase
from movai_core_shared.core.zmq.zmq_client import ZMQClient, AsyncZMQClient
from movai_core_shared.core.zmq.zmq_subscriber import ZMQSubscriber, AsyncZMQSubscriber
from movai_core_shared.core.zmq.zmq_publisher import ZMQPublisher, AsyncZMQPublisher
from movai_core_shared.core.zmq.zmq_helpers import generate_zmq_identity
from movai_core_shared.exceptions import ArgumentError


class ZMQManager:
    _logger = getLogger("ZMQManager")
    _clients = {}
    _async_clients = {}
    _publishers = {}
    _async_publishers = {}
    _subscribers = {}
    _async_subscribers = {}

    @classmethod
    def validate_server_addr(cls, server_addr: str):
        if not isinstance(server_addr, str):
            error_msg = "The argument server_addr must be of type string"
            cls._logger.error(error_msg)
            raise ArgumentError(error_msg)

    def validate_zmq_type(cls, zmq_object: ZMQBase):
        if not isinstance(zmq_object, ZMQBase):
            error_msg = f"The argument zmq_object must be of type {ZMQBase.__class__.__name__}"
            cls._logger.error(error_msg)
            raise ArgumentError(error_msg)

    @classmethod
    def _get_zmq_object(cls, server_addr: str, object_type: ZMQBase, objects_dict: dict) -> ZMQBase:
        cls.validate_server_addr(server_addr)
        
        if server_addr in objects_dict:
            return objects_dict[server_addr]
        
        else:
            identity = ""
            if isinstance(object_type, ZMQClient) or isinstance(object_type, AsyncZMQClient):
                identity = generate_zmq_identity("dealer")
            elif isinstance(object_type, ZMQSubscriber) or isinstance(object_type, AsyncZMQSubscriber):
                identity = generate_zmq_identity("sub")
            elif isinstance(object_type, ZMQPublisher) or isinstance(object_type, AsyncZMQPublisher):
                identity = generate_zmq_identity("pub")
            else:
                identity = generate_zmq_identity("")
            zmq_object = object_type(identity, server_addr)
            objects_dict[server_addr] = zmq_object
            return zmq_object

    @classmethod
    def get_client(cls, server_addr: str) -> ZMQClient:
        client = cls._get_zmq_object(server_addr, ZMQClient, cls._clients)
        return client

    @classmethod
    def get_async_client(cls, server_addr: str) -> AsyncZMQClient:
        client = cls._get_zmq_object(server_addr, AsyncZMQClient, cls._async_clients)
        return client

    @classmethod
    def get_subscriber(cls, server_addr: str) -> ZMQSubscriber:
        subscriber = cls._get_zmq_object(server_addr, ZMQSubscriber, cls._subscribers)
        return subscriber

    @classmethod
    def get_async_subscriber(cls, server_addr: str) -> AsyncZMQSubscriber:
        subscriber = cls._get_zmq_object(server_addr, AsyncZMQSubscriber, cls._async_subscribers)
        return subscriber

    @classmethod
    def get_publisher(cls, server_addr: str) -> ZMQPublisher:
        publisher = cls._get_zmq_object(server_addr, ZMQPublisher, cls._publishers)
        return publisher

    @classmethod
    def get_async_publisher(cls, server_addr: str) -> AsyncZMQPublisher:
        publisher = cls._get_zmq_object(server_addr, AsyncZMQPublisher, cls._async_publishers)
        return publisher
