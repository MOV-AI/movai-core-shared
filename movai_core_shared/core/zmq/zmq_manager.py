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
from enum import Enum
from logging import getLogger
from typing import Dict, Type, TypedDict

from beartype import beartype

from movai_core_shared.core.zmq.zmq_base import ZMQBase
from movai_core_shared.core.zmq.zmq_client import ZMQClient, AsyncZMQClient
from movai_core_shared.core.zmq.zmq_subscriber import ZMQSubscriber, AsyncZMQSubscriber
from movai_core_shared.core.zmq.zmq_publisher import ZMQPublisher, AsyncZMQPublisher
from movai_core_shared.core.zmq.zmq_helpers import generate_zmq_identity
from movai_core_shared.envvars import MOVAI_ZMQ_SHUTDOWN_LINGER_MS
from movai_core_shared.exceptions import ArgumentError

# how long the shutdown waits for a client in use
SHUTDOWN_LOCK_TIMEOUT_S = 0.1


class ZMQType(Enum):
    CLIENT = 1
    ASYNC_CLIENT = 2
    PUBLISHER = 3
    ASYNC_PUBLISHER = 4
    SUBSCRIBER = 5
    ASYNC_SUBSCRIBER = 6


class ZMQTypeValue(TypedDict):
    type: Type[ZMQClient]
    identity: str


ZMQ_TYPES: Dict[ZMQType, ZMQTypeValue] = {
    ZMQType.CLIENT: {"type": ZMQClient, "identity": "dealer"},
    ZMQType.ASYNC_CLIENT: {"type": AsyncZMQClient, "identity": "dealer"},
    ZMQType.PUBLISHER: {"type": ZMQPublisher, "identity": "pub"},
    ZMQType.ASYNC_PUBLISHER: {"type": AsyncZMQPublisher, "identity": "pub"},
    ZMQType.SUBSCRIBER: {"type": ZMQSubscriber, "identity": "sub"},
    ZMQType.ASYNC_SUBSCRIBER: {"type": AsyncZMQSubscriber, "identity": "sub"},
}


class ZMQManager:
    """This class will host ZMQ objects by their type and address."""

    _logger = getLogger("ZMQManager")
    _clients: Dict[ZMQType, Dict[str, ZMQClient]] = {
        ZMQType.CLIENT: {},
        ZMQType.ASYNC_CLIENT: {},
        ZMQType.PUBLISHER: {},
        ZMQType.ASYNC_PUBLISHER: {},
        ZMQType.SUBSCRIBER: {},
        ZMQType.ASYNC_SUBSCRIBER: {},
    }

    @classmethod
    def validate_server_addr(cls, server_addr: str):
        if not isinstance(server_addr, str):
            error_msg = "The argument server_addr must be of type string"
            cls._logger.error(error_msg)
            raise ArgumentError(error_msg)

    @classmethod
    @beartype
    def _get_or_create_zmq_object(cls, server_addr: str, zmq_type: ZMQType) -> ZMQClient:
        if zmq_type not in cls._clients:
            raise TypeError(f"{zmq_type} does not exist!")

        if server_addr in cls._clients[zmq_type]:
            return cls._clients[zmq_type][server_addr]

        identity_type = ZMQ_TYPES[zmq_type]["identity"]
        identity = generate_zmq_identity(identity_type)
        zmq_object = ZMQ_TYPES[zmq_type]["type"](identity, server_addr)
        cls._clients[zmq_type][server_addr] = zmq_object
        return zmq_object

    @classmethod
    def get_client(cls, server_addr: str, client_type: ZMQType) -> ZMQClient:
        client = cls._get_or_create_zmq_object(server_addr, client_type)
        return client

    @classmethod
    def shutdown(cls, linger_ms: int = MOVAI_ZMQ_SHUTDOWN_LINGER_MS) -> None:
        """Sends the messages still queued on the synchronous zmq objects, then closes them.

        Blocks until all the queued messages are sent or `linger_ms` elapses.
        Called automatically when the interpreter exits.

        Args:
            linger_ms (int): How long to wait for the queued messages to be sent.
        """
        sync_types = (ZMQType.CLIENT, ZMQType.PUBLISHER, ZMQType.SUBSCRIBER)
        locks = []
        try:
            # all the zmq objects using the context, also the ones not created by the manager
            for zmq_object in ZMQBase.instances():
                if zmq_object.lock is None:
                    zmq_object.close(linger_ms)
                elif zmq_object.lock.acquire(timeout=SHUTDOWN_LOCK_TIMEOUT_S):
                    locks.append(zmq_object.lock)
                    zmq_object.close(linger_ms)
                else:
                    # busy, e.g. waiting for a message: the termination interrupts it and it
                    # closes its socket itself, with the linger set before the termination
                    zmq_object.set_linger(linger_ms)
            if not ZMQBase.context.closed:
                # waits for the closed sockets to send their queued messages, up to their linger
                ZMQBase.context.term()
        finally:
            for lock in locks:
                lock.release()

        # dropping the last reference to a client closes its socket without a linger
        for zmq_type in sync_types:
            cls._clients[zmq_type].clear()


# pyzmq doesn't terminate the context when the interpreter exits,
# so the messages still queued (sent right before exiting) would be lost
atexit.register(ZMQManager.shutdown)
