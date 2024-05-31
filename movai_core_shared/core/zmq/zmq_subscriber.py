"""
   Copyright (C) Mov.ai  - All Rights Reserved
   Unauthorized copying of this file, via any medium is strictly prohibited
   Proprietary and confidential

   Usage:
        Basic 0MQ client for connecting 0MQ servers.

   Developers:
   - Erez Zomer (erez@mov.ai) - 2023
"""
import zmq
import zmq.asyncio

from movai_core_shared.core.zmq.zmq_client import ZMQClient, AsyncZMQClient


class ZMQSubscriber(ZMQClient):
    """A very basic implementation of ZMQ Subscriber"""

    zmq_socket_type = zmq.SUB


class AsyncZMQSubscriber(AsyncZMQClient):
    """An Async implementation of ZMQ subscriber"""

    zmq_socket_type = zmq.SUB
