"""
   Copyright (C) Mov.ai  - All Rights Reserved
   Unauthorized copying of this file, via any medium is strictly prohibited
   Proprietary and confidential

   Usage:
        Basic 0MQ client for connecting 0MQ servers.

   Developers:
   - Erez Zomer (erez@mov.ai) - 2022
"""
from abc import ABC
from logging import getLogger

import zmq




class ZMQBase(ABC):

    _ctx = zmq.Context()

    def __init__(self, identity: str, address: str, debug: bool = False) -> None:
        """Initializes the object and the connection to the server.

        Args:
            identity (str): A unique identity.
            addr (str): The addr to connect or bind to.
            debug (bool): A flag which indicates debug mode.
        """
        self._logger = getLogger(self.__class__.__name__)
        self._identity = identity.encode("utf-8")
        self._addr = address
        self._debug = debug
        self._lock = None
        self._socket = None
