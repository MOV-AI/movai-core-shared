import asyncio
import logging
import pytest
import os
import psutil
import socket
import time
import threading
import zmq

from time import sleep
from tests.common.zmq_server import TestServer, TEST_SERVER_ADDR, SimpleRequest

from movai_core_shared.core.zmq.zmq_client import ZMQClient, AsyncZMQClient

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)
LOGGER.addHandler(logging.StreamHandler())

PERF_TEST_REQUESTS = 100
PERF_TEST_RESULTS_DIR = "perf_results"


@pytest.mark.test_zmq
class TestZMQClients:
    server = None
    server_thread = None
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

    @pytest.fixture(scope="class", autouse=True)
    def setup(self):
        """Setup the test server"""
        LOGGER.info("Starting test server in a separate thread")
        self.server = TestServer(LOGGER)
        self.server_thread = threading.Thread(target=self.server.start, args=(), daemon=True)
        self.server_thread.start()
        sleep(2)
        yield

    @pytest.fixture(scope="class")
    def teardown(self):
        """Teardown the test server"""
        LOGGER.info("Stopping test server")
        self.server.stop()
        self.server_thread.join()
        yield

    @pytest.fixture(scope="class", autouse=True)
    def create_results_dir(self):
        """Create the results directory"""
        if not os.path.exists(PERF_TEST_RESULTS_DIR):
            os.makedirs(PERF_TEST_RESULTS_DIR)
        else:
            # remove its contents
            for file in os.listdir(PERF_TEST_RESULTS_DIR):
                os.remove(os.path.join(PERF_TEST_RESULTS_DIR, file))
        yield

    def list_unix_sockets(self, type="STREAMING", path=TEST_SERVER_ADDR.split("://")[-1]):
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
                        if conn.type == socket.SOCK_STREAM:
                            return True
                        else:
                            # break the loop if the socket is found but not the correct type
                            LOGGER.debug(
                                f"Found socket {conn.laddr} with type {conn.type} but expected {type}"
                            )
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
                LOGGER.info("Unix socket is found")
                return True
            else:
                LOGGER.error("Unix socket is found but not of type STREAMING")
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
        assert self.check_existing_unix_socket(), "Unix socket is not found"
        assert client._socket is not None, "Socket is not initialized"

        client._socket.close()

        client.reset(force=force)
        sleep(1)
        assert self.check_existing_unix_socket(), "Unix socket is not found after reset"
        assert client._socket is not None, "Socket is not initialized after reset"

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

        LOGGER.debug("Sending dummy request")
        try:
            await async_client.send(self.dummy_request, use_lock=use_lock)
        except zmq.error.ZMQError as e:
            LOGGER.error(f"Got exception: {e}")
            assert False, f"Got ZMQ exception: {e}"
        except Exception as e:
            LOGGER.error(f"Got exception: {e}")
            assert False, f"Got exception: {e}"

        del async_client
        sleep(1)

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

        if valid_request.get("response_required", False):
            # check socket is ready to receive
            assert self.check_existing_unix_socket()

            LOGGER.debug("Waiting for response")
            response = await async_client.receive(use_lock=use_lock)
            assert response is not None
            LOGGER.debug("Received response: %s", response)
            # assert response["status"] == "Got request & successfully proccessed"

        del async_client
        sleep(1)

    @pytest.mark.asyncio
    @pytest.mark.parametrize("use_lock", [True, False])
    async def test_sync_dummy_req(self, use_lock):
        """Test if the ZMQClient can send a dummy request without waiting a response"""
        LOGGER.info("--- Testing ZMQClient with dummy request ---")
        sync_client = ZMQClient("dealer", TEST_SERVER_ADDR)
        sync_client.init_socket()

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
            sync_client.send(dummy_request, use_lock=use_lock)
        except zmq.error.ZMQError as e:
            LOGGER.error(f"Got exception: {e}")
            assert False, f"Got ZMQ exception: {e}"
        except Exception as e:
            LOGGER.error(f"Got exception: {e}")
            assert False, f"Got exception: {e}"

        del sync_client

    @pytest.mark.parametrize("use_lock", [True, False])
    def test_sync_valid_req(self, use_lock):
        """Test if the ZMQClient can send a valid request and receive a response"""
        LOGGER.info("--- Testing ZMQClient with valid request ---")
        sync_client = ZMQClient("dealer", TEST_SERVER_ADDR)
        sync_client.init_socket()

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
            sync_client.send(valid_request, use_lock=use_lock)
        except zmq.error.ZMQError as e:
            LOGGER.error(f"Got exception: {e}")
            assert False, f"Got ZMQ exception: {e}"
        except Exception as e:
            LOGGER.error(f"Got exception: {e}")
            assert False, f"Got exception: {e}"

        if valid_request.get("response_required", False):
            # check socket is ready to receive
            assert self.check_existing_unix_socket()

            LOGGER.debug("Waiting for response")
            response = sync_client.receive(use_lock=use_lock)
            assert response is not None
            LOGGER.debug("Received response: %s", response)

            # assert response["status"] == "Got request & successfully proccessed"

        del sync_client

    @pytest.mark.test_zmq_perf
    @pytest.mark.asyncio
    @pytest.mark.parametrize("use_lock", [True])
    async def test_perf_async_client(self, use_lock, nb_requests=PERF_TEST_REQUESTS):
        """Test the performance of the AsyncZMQClient by sending multiple requests
        Will send multiple requests to the server and check the performance of the client
        by measuring the time taken to send the requests.

        Args:
            nb_requests (int): The number of requests to send

        """
        LOGGER.info("--- Testing performance of AsyncZMQClient ---")
        async_client = AsyncZMQClient("dealer", TEST_SERVER_ADDR)
        async_client.init_socket()

        valid_request = SimpleRequest(
            req_data={"msg": "log"},
            req_type="async_perf_test",
            created=0,
            response_required=True,
            robot_info={"fleet": "fleet", "robot": "robot", "service": "service", "id": "id"},
        ).model_dump()

        LOGGER.debug(f"Sending {nb_requests} requests")
        start_time = time.time()
        for _ in range(nb_requests):
            valid_request.update({"req_id": f"req_{_}"})
            await async_client.send(valid_request, use_lock=use_lock)
        end_time = time.time()
        LOGGER.debug(f"Sent {nb_requests} requests in {end_time - start_time} seconds")

        assert end_time - start_time < 10, "Sending requests took too long"
        # test average time to send a request
        assert (end_time - start_time) / nb_requests < 0.001, "Sending requests took too long"

        # print performance to file
        with open(os.path.join(PERF_TEST_RESULTS_DIR, "async_client_perf.txt"), "a") as f:
            f.write(f"addr,nb_requests,test_time,average\n")
            f.write(
                f"{TEST_SERVER_ADDR},{nb_requests},{end_time - start_time},{(end_time - start_time) / nb_requests}\n"
            )

        del async_client

    @pytest.mark.test_zmq_perf
    @pytest.mark.parametrize("use_lock", [True])
    def test_multithread_perf_sync_client(
        self, use_lock, nb_requests=PERF_TEST_REQUESTS, nb_threads=10
    ):
        """Test the performance of the ZMQClient by sending multiple requests in multiple threads
        Will send multiple requests to the server and check the performance of the client
        by measuring the time taken to send the requests in multiple threads.

        Args:
            nb_requests (int): The number of requests to send
            nb_threads (int): The number of threads to use

        """
        LOGGER.info(f"--- Testing performance of ZMQClient in {nb_threads} threads ---")
        threads = []

        # launch multiple async clients in multiple threads
        for i in range(nb_threads):
            thread = threading.Thread(target=self._send_requests, args=(i, nb_requests, use_lock))
            threads.append(thread)
            thread.start()

        # wait for all threads to finish
        for thread in threads:
            thread.join()

    def _send_requests(self, thread_id, nb_requests, use_lock):
        """Send multiple requests in a thread"""
        sync_client = ZMQClient(f"dealer_{thread_id}", TEST_SERVER_ADDR)
        sync_client.init_socket()

        valid_request = SimpleRequest(
            req_data={"msg": "log"},
            req_type="sync_perf_test",
            created=0,
            response_required=True,
            robot_info={"fleet": "fleet", "robot": "robot", "service": "service", "id": "id"},
        ).model_dump()

        LOGGER.debug(f"Thread {thread_id} sending {nb_requests} requests")
        start_time = time.time()
        for _ in range(nb_requests):
            valid_request.update({"req_id": f"req_{_}"})
            sync_client.send(valid_request, use_lock=use_lock)
        end_time = time.time()
        LOGGER.debug(
            f"Thread {thread_id} sent {nb_requests} requests in {end_time - start_time} seconds"
        )

        assert end_time - start_time < 10, "Sending requests took too long"
        # test average time to send a request
        assert (end_time - start_time) / nb_requests < 0.001, "Sending requests took too long"

        # print performance to file with thread id
        with open(
            os.path.join(PERF_TEST_RESULTS_DIR, f"multithread_{thread_id}_client_perf.txt"), "a"
        ) as f:
            f.write(f"addr,nb_requests,test_time,average,thread_id\n")
            f.write(
                f"{TEST_SERVER_ADDR},{nb_requests},{end_time - start_time},{(end_time - start_time) / nb_requests},{thread_id}\n"
            )

        del sync_client

    @pytest.mark.test_zmq_perf
    @pytest.mark.asyncio
    @pytest.mark.parametrize("use_lock", [True])
    async def test_multithread_perf_async_client(
        self, use_lock, nb_requests=PERF_TEST_REQUESTS, nb_threads=10
    ):
        """Test the performance of the AsyncZMQClient by sending multiple requests in multiple threads
        Will send multiple requests to the server and check the performance of the client
        by measuring the time taken to send the requests in multiple threads.

        Args:
            nb_requests (int): The number of requests to send
            nb_threads (int): The number of threads to use

        """
        LOGGER.info(f"--- Testing performance of AsyncZMQClient in {nb_threads} threads ---")
        threads = []

        # launch multiple async clients in multiple threads
        for i in range(nb_threads):
            thread = threading.Thread(
                target=self._send_requests_async, args=(i, nb_requests, use_lock)
            )
            threads.append(thread)
            thread.start()

        # wait for all threads to finish
        for thread in threads:
            thread.join()

    async def _send_requests_async(self, thread_id, nb_requests, use_lock):
        """Send multiple requests in a thread"""
        async_client = AsyncZMQClient(f"dealer_{thread_id}", TEST_SERVER_ADDR)
        async_client.init_socket()

        valid_request = SimpleRequest(
            req_data={"msg": "log"},
            req_type="async_perf_test",
            created=0,
            response_required=True,
            robot_info={"fleet": "fleet", "robot": "robot", "service": "service", "id": "id"},
        ).model_dump()

        LOGGER.debug(f"Thread {thread_id} sending {nb_requests} requests")
        start_time = time.time()
        for _ in range(nb_requests):
            valid_request.update({"req_id": f"req_{_}"})
            asyncio.run(async_client.send(valid_request, use_lock=use_lock))
        end_time = time.time()
        LOGGER.debug(
            f"Thread {thread_id} sent {nb_requests} requests in {end_time - start_time} seconds"
        )

        assert end_time - start_time < 10, "Sending requests took too long"
        # test average time to send a request
        assert (end_time - start_time) / nb_requests < 0.001, "Sending requests took too long"

        # print performance to file with thread id
        with open(
            os.path.join(PERF_TEST_RESULTS_DIR, f"multithread_{thread_id}_async_client_perf.txt"),
            "a",
        ) as f:
            f.write(f"addr,nb_requests,test_time,average,thread_id\n")
            f.write(
                f"{TEST_SERVER_ADDR},{nb_requests},{end_time - start_time},{(end_time - start_time) / nb_requests},{thread_id}\n"
            )

        del async_client
