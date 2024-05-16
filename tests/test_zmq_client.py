import logging
import pytest
import os
import psutil
import socket
import threading
import zmq

from time import sleep
from tests.common.zmq_server import TestServer, TEST_SERVER_ADDR, SimpleRequest

from movai_core_shared.core.zmq.zmq_client import ZMQClient, AsyncZMQClient

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)
LOGGER.addHandler(logging.StreamHandler())


@pytest.mark.test_zmq
class TestZMQClients:
    server = None
    server_thread = None

    @pytest.fixture(scope="class", autouse=True)
    def setup(self):
        """Setup the test server"""
        LOGGER.info("Starting test server in a separate thread")
        self.server = TestServer(LOGGER)
        self.server_thread = threading.Thread(target=self.server.start, args=(), daemon=True)
        self.server_thread.start()
        sleep(2)
        yield

    def list_unix_sockets(type="STREAMING", path=TEST_SERVER_ADDR.split("://")[-1]):
        """List all the UNIX sockets for the given type and path
        Args:
            type (str): The type of the socket to check
            path (str): The path to check for the socket
        Returns:
            bool: True if the socket is found with correct type, False otherwise
        """
        for proc in psutil.process_iter(["pid", "name"]):
            try:
                # Get UNIX socket connections for the process
                connections = proc.connections(kind="unix")
                for conn in connections:
                    if path in conn.laddr:
                        LOGGER.debug(
                            f"PID: {proc.info['pid']}, Process Name: {proc.info['name']}, Path: {conn.laddr}, Type: {conn.type}, Status: {conn}"
                        )
                        if conn.type == socket.SOCK_STREAM:
                            return True
                        else:
                            # break the loop if the socket is found but not the correct type
                            return False
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass

        return False

    def check_existing_unix_socket(self):
        """Check if the unix socket is existing
        Args:
            type (str): The type of the socket to check
        Returns:
            bool: True if the socket is found with correct type, False otherwise
        """
        ret = False
        path = TEST_SERVER_ADDR.split("://")[-1]

        if os.path.exists(path):
            # check if the socket is listening or established
            ret = self.list_unix_sockets()
            if ret:
                LOGGER.info(f"Unix socket is found")
                return True
            else:
                LOGGER.error(f"Unix socket is found but not of type STREAMING")
                return False
        else:
            LOGGER.error("Unix socket is not found")
            return False

    def test_server_socket_exists(self):
        """Test if the server socket is existing"""
        assert self.check_existing_unix_socket()

    @pytest.mark.parametrize("force", [True, False])
    def test_sync_client_socket_reset(self, force):
        """Test if the ZMQClient execute reset correctly after closing"""
        client = ZMQClient("TEST_CLIENT", addr=TEST_SERVER_ADDR)
        client.init_socket()
        assert self.check_existing_unix_socket()
        assert client._socket is not None

        client._socket.close()

        client.reset(force=force)
        sleep(1)
        assert self.check_existing_unix_socket()
        assert client._socket is not None

    @pytest.mark.parametrize("force", [True, False])
    def test_async_client_socket_reset(self, force):
        """Test if the AsyncZMQClient execute reset correctly after closing"""
        client = AsyncZMQClient("TEST_CLIENT", addr=TEST_SERVER_ADDR)
        client.init_socket()
        assert self.check_existing_unix_socket()
        assert client._socket is not None

        client._socket.close()

        client.reset(force=force)
        sleep(1)
        assert self.check_existing_unix_socket()
        assert client._socket is not None

    @pytest.mark.asyncio
    @pytest.mark.parametrize("use_lock", [True, False])
    async def test_async_dummy_req(self, use_lock):
        """Test if the AsyncZMQClient can send a dummy request without waiting a response"""
        LOGGER.info("--- Testing AsyncZMQClient with dummy request ---")
        async_client = AsyncZMQClient("dealer", TEST_SERVER_ADDR)
        async_client.init_socket()

        dummy_request = {
            "request": {
                "req_type": "test",
                "created": 0,
                "response_required": True,
                "req_data": {"msg": "async_request"},
                "robot_info": {
                    "fleet": "fleet",
                    "robot": "robot",
                    "service": "service",
                    "id": "id",
                },
            }
        }
        LOGGER.debug(f"Sending request: {dummy_request}")

        # catch exception
        try:
            await async_client.send(dummy_request, use_lock=use_lock)
        except zmq.error.ZMQError as e:
            LOGGER.error(f"Got exception: {e}")
            assert False, f"Got ZMQ exception: {e}"
        except Exception as e:
            LOGGER.error(f"Got exception: {e}")
            assert False, f"Got exception: {e}"

        del async_client

    @pytest.mark.asyncio
    @pytest.mark.parametrize("use_lock", [True, False])
    async def test_async_valid_req(self, use_lock):
        """Test if the AsyncZMQClient can send a valid request and receive a response"""
        LOGGER.info("--- Testing AsyncZMQClient with valid request ---")
        async_client = AsyncZMQClient("dealer", TEST_SERVER_ADDR)
        async_client.init_socket()

        valid_request = SimpleRequest(
            req_data={"msg": "log"},
            req_type="test",
            created=0,
            response_required=True,
            robot_info={"fleet": "fleet", "robot": "robot", "service": "service", "id": "id"},
        ).model_dump()
        LOGGER.debug(f"Sending request: {valid_request}")

        # catch exception
        try:
            await async_client.send(valid_request, use_lock=use_lock)
        except zmq.error.ZMQError as e:
            LOGGER.error(f"Got exception: {e}")
            assert False, f"Got ZMQ exception: {e}"
        except Exception as e:
            LOGGER.error(f"Got exception: {e}")
            assert False, f"Got exception: {e}"

        sleep(1)

        if valid_request.get("response_required", False):
            # check socket is ready to receive
            assert self.check_existing_unix_socket()

            LOGGER.debug("Waiting for response")
            response = await async_client.receive(use_lock=use_lock)
            assert response is not None
            LOGGER.debug("Received response: %s", response)
            assert response["status"] == "ok"

        del async_client
