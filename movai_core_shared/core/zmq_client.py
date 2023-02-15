"""
   Copyright (C) Mov.ai  - All Rights Reserved
   Unauthorized copying of this file, via any medium is strictly prohibited
   Proprietary and confidential

   Usage:
        Basic 0MQ client for connecting 0MQ servers.

   Developers:
   - Erez Zomer (erez@mov.ai) - 2022
"""
import json
import os

import zmq.asyncio

from movai_core_shared.core.secure import create_client_keys
from movai_core_shared.envvars import (
    MOVAI_ZMQ_TIMEOUT_MS
)
from movai_core_shared.exceptions import (
    MessageError,
    MessageFormatError
)




class ZMQClient:
    """
    A ZMQ client to communicate with zmq protocol
    """

    def __init__(
        self,
        server_ip: str = "",
        server_port: str = "",
        server_pub_key: str = "",
        identity: str = f"uid_{os.getuid()}",
        timeout_ms: int = MOVAI_ZMQ_TIMEOUT_MS,
    ) -> None:
        """Constractor for zmq client

        Args:
            server_ip: the dest ip in string
            server_port: the dest port in string
            server_pub_key: public key of the dest, default to "" which means no encryption
            name: name of the client, default for process id
            timeout_ms: timeout in miliseconds, to drop message, default = 0 to infinite timeout

        Returns:
            None: None

        Raise: 
            OSError if the zmq socket failed to create
        """
        self.ctx = zmq.Context()
        self._socket = self.ctx.socket(zmq.DEALER)
        self._socket.identity = identity.encode("utf8")
        if timeout_ms != 0:
            self._socket.setsockopt(zmq.RCVTIMEO, timeout_ms)
        addr = f"tcp://{server_ip}:{server_port}"
        if server_pub_key != "":
            self._socket.curve_serverkey = server_pub_key
            self._my_pub, self._socket.curve_secretkey = create_client_keys("/tmp/", identity)
            self._socket.curve_publickey = self._my_pub
        else:
            self._my_pub = ""
        self._socket.connect(addr)

    def __del__(self):
        """closes the socket when the object is destroyed.
        """
        self._socket.close()

    def get_pub_key(self) -> str:
        """Get the public key generate by this class

        Returns:
            str: the public key
        """
        return self._my_pub

    def send_msg(self, msg: dict) -> dict:
        """send fucntion

        send message to the zmq server
        socket will wait for response

        Args:
            msg: the message in dict
            wait_for_response (bool): should it wait for response, or not, default True

        Returns:
            dict: response in dict
        """
        try:
            raw_data = json.dumps(msg).encode("utf8")
            self._socket.send(raw_data)
            response = {"info": "sent message successfully."}
        except FileNotFoundError:
            response = {"error": "can't send to server, check that it is running"}
        except OSError as err:
            response = {"error": str(err)}
        except json.JSONDecodeError:
            response = {"error": "can't parse data from server."}
        except zmq.error.Again:
            response = {
                "error": "movai socket doesn't respond,\n"
                + "please check that the service is running with:"
                + "'service movai-service status'"
            }
        return response

    def rcv_msg(self) -> dict:
        """
        Recieves a message response over ZeroMQ from the server.

        Raises:
            MessageFormatError: In case the response message format is wrong.
            MessageError: In case response is empty.

        Returns:
            dict: The response from the server.
        """
        response = self._socket.recv_multipart()
        index = len(response) - 1
        buffer = response[index]

        if buffer is None:
            raise MessageError("Got an empty response!")

        msg = json.loads(buffer)
        # check for request in request
        if "response" not in msg:
            raise MessageFormatError(f"The message format is unknown: {msg}.")
        response_msg = msg["response"]
        return response_msg
