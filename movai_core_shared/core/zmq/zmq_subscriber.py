"""
   Copyright (C) Mov.ai  - All Rights Reserved
   Unauthorized copying of this file, via any medium is strictly prohibited
   Proprietary and confidential

   Usage:
        Basic 0MQ client for connecting 0MQ servers.

   Developers:
   - Erez Zomer (erez@mov.ai) - 2023
"""
from typing import Optional

import zmq

from movai_core_shared.core.zmq.zmq_client import ZMQClient, AsyncZMQClient


class ZMQSubscriber(ZMQClient):
    """A very basic implementation of ZMQ Subscriber"""

    zmq_socket_type = zmq.SUB

    def close(self, linger_ms: Optional[int] = None) -> None:
        """Closes the socket right away, a subscriber only sends its subscriptions.

        Args:
            linger_ms (int): Ignored, there are no messages to send.
        """
        super().close(linger_ms=0)

    def set_linger(self, linger_ms: int) -> None:
        """Keeps no linger, a subscriber only sends its subscriptions.

        Args:
            linger_ms (int): Ignored, there are no messages to send.
        """


class AsyncZMQSubscriber(AsyncZMQClient):
    """An Async implementation of ZMQ subscriber"""

    zmq_socket_type = zmq.SUB
