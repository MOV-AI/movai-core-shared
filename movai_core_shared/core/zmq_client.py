"""
   Copyright (C) Mov.ai  - All Rights Reserved
   Unauthorized copying of this file, via any medium is strictly prohibited
   Proprietary and confidential

   Usage:
        Basic 0MQ client for connecting 0MQ servers.

   Developers:
   - Erez Zomer (erez@mov.ai) - 2022
"""
import asyncio
import json
import os
from stat import S_IRGRP, S_IROTH, S_IRUSR

import zmq
from movai_core_shared import Log
from movai_core_shared.envvars import MOVAI_ZMQ_IP, MOVAI_ZMQ_SOCKET
from zmq.asyncio import Context


class ZmqClient:
    """
    A ZMQ client to communicate with zmq protocol
    """

    def __init__(
        self,
        ip: str = MOVAI_ZMQ_IP,
        port: str = MOVAI_ZMQ_SOCKET,
        pub_key: str = "",
        name: str = "",
        timeout_ms: int = 0,
    ) -> None:
        """Constractor for zmq client

        Args:
            ip: the dest ip in string
            port: the dest port in string
            pub_key: public key of the dest, default to "" which means no encryption
            name: name of the client, default for process id
            timeout_ms: timeout in miliseconds, to drop message, default = 0 to infinite timeout

        Returns:
            None: None
        """
        self.log = Log.get_logger("zmq socket")
        try:
            self.ctx = zmq.Context()
            self.sock = self.ctx.socket(zmq.DEALER)
            if name == "":
                name = f"uid_{os.getuid()}"
            self.sock.identity = name.encode("utf8")
            if timeout_ms != 0:
                self.sock.setsockopt(zmq.RCVTIMEO, timeout_ms)
            addr = f"tcp://{ip}:{port}"
            if pub_key != "":
                self.sock.curve_publickey = pub_key
                self.__my_pub, self.sock.curve_secretkey = create_certificates(
                    "/tmp/", "key"
                )
            else:
                self.__my_pub = ""
            self.sock.bind(addr)
        except OSError as e:
            self.log.error("failed to bind zmq socket")
            self.log.error(e)

    def get_pub_key(self) -> str:
        """Get the public key generate by this class

        Returns:
            str: the public key
        """
        return self.__my_pub

    def send_msg(self, msg: dict, wait_for_response=True) -> dict:
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
            self.sock.send(raw_data)
            msg_data = bytearray()
            if not wait_for_response:
                return "Didn't wait for response"
            response = self.sock.recv()
            msg_data.extend(response)
            response = json.loads(msg_data.decode())

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


def create_certificates(key_dir, name):
    """Create zmq certificates.
    Returns the file paths to the public and secret certificate files.
    """
    base_filename = os.path.join(key_dir, name)
    if os.path.exists(f"{base_filename}.public") and os.path.exists(
        f"{base_filename}.secret"
    ):
        with open(base_filename + ".public", "r", encoding="utf8") as f:
            public_key = f.readlines()[0]
        with open(base_filename + ".secret", "r", encoding="utf8") as f:
            secret_key = f.readlines()[0]
    else:
        public_key, secret_key = zmq.curve_keypair()
        with open(base_filename + ".public", "w", encoding="utf8") as f:
            f.write(public_key.decode("utf8"))
            os.chmod(base_filename + ".public", S_IRUSR | S_IRGRP | S_IROTH)
        with open(base_filename + ".secret", "w", encoding="utf8") as f:
            f.write(secret_key.decode("utf8"))
            os.chmod(base_filename + ".secret", S_IRUSR)

    return public_key, secret_key
