"""Tests that ZMQ clients match each response to the request that produced it.

Several requests can be in flight on the same client socket (ZMQManager shares one client
per address in a process), and servers answer them in the order they finish.
"""

import asyncio
import json
import random
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from typing import List

import pytest

from movai_core_shared.core.message_client import AsyncMessageClient, MessageClient
from movai_core_shared.core.zmq import zmq_client
from movai_core_shared.core.zmq.zmq_client import AsyncZMQClient, ZMQClient
from movai_core_shared.core.zmq.zmq_server import ZMQServer

RECV_TIMEOUT_MS = 1000


class DelayedEchoServer(ZMQServer):
    """Handles every request in its own task (like message-server) and answers after
    the requested delay, so responses go out in a different order than the requests.

    Reads the payload from the last frame and sends back the other frames,
    like message-server's BaseDispatcher.
    """

    def payload_index(self, buffer: List[bytes]) -> int:
        return len(buffer) - 1

    async def handle(self, buffer: List[bytes]) -> None:
        index = self.payload_index(buffer)
        request = json.loads(buffer[index])["request"]
        if not request["response_required"]:
            return
        await asyncio.sleep(request["req_data"]["delay"])
        buffer[index] = json.dumps({"response": {"id": request["req_data"]["id"]}}).encode()
        await self._socket.send_multipart(buffer)


class SpawnerLikeServer(DelayedEchoServer):
    """Picks the payload frame like flow-initiator's SpawnerServer."""

    def payload_index(self, buffer: List[bytes]) -> int:
        return 2 if len(buffer) == 3 else 1


def make_request(req_id, delay=0.0, response_required=True) -> dict:
    return {
        "request": {
            "req_type": "test",
            "created": 0,
            "response_required": response_required,
            "req_data": {"id": req_id, "delay": delay},
            "robot_info": {"fleet": "fleet", "robot": "robot", "service": "service", "id": ""},
        }
    }


def response_id(response: dict):
    return response.get("response", {}).get("id")


@pytest.fixture(autouse=True)
def short_recv_timeout(monkeypatch):
    monkeypatch.setattr(zmq_client, "MOVAI_ZMQ_RECV_TIMEOUT_MS", RECV_TIMEOUT_MS)


@pytest.fixture(params=[DelayedEchoServer, SpawnerLikeServer])
def server_addr(request, tmp_path):
    addr = f"ipc://{tmp_path}/server.sock"
    server = request.param(request.param.__name__, addr)
    thread = threading.Thread(target=server.start, daemon=True)
    thread.start()
    time.sleep(0.3)
    yield addr
    server.stop()


@pytest.mark.asyncio
async def test_async_message_clients_get_own_response(server_addr):
    """Like the backend serving concurrent log queries, one per robot."""

    async def one(i):
        # a new message client per call still shares the ZMQ client of the address
        client = AsyncMessageClient(server_addr)
        data = {"id": i, "delay": random.uniform(0, 0.05)}
        return i, await client.send_request("test", data, response_required=True)

    results = await asyncio.gather(*(one(i) for i in range(50)))

    assert [(i, response_id(resp)) for i, resp in results] == [(i, i) for i in range(50)]


def test_message_client_threads_get_own_response(server_addr):
    client = MessageClient(server_addr)

    def one(i):
        data = {"id": i, "delay": random.uniform(0, 0.01)}
        return i, client.send_request("test", data, response_required=True)

    with ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(one, range(50)))

    assert [(i, response_id(resp)) for i, resp in results] == [(i, i) for i in range(50)]


@pytest.mark.asyncio
async def test_async_concurrent_requests_get_own_response(server_addr):
    client = AsyncZMQClient("async_concurrent", server_addr)

    async def one(i):
        return i, await client.request(make_request(i, delay=random.uniform(0, 0.05)))

    results = await asyncio.gather(*(one(i) for i in range(200)))

    assert [(i, response_id(resp)) for i, resp in results] == [(i, i) for i in range(200)]
    # nothing is left waiting on the socket once all requests are answered
    assert not client._pending
    assert client._reader is None


@pytest.mark.asyncio
async def test_async_late_response_is_not_returned_to_next_request(server_addr):
    client = AsyncZMQClient("async_late", server_addr)

    # answered after the client gave up on it
    assert await client.request(make_request("slow", delay=1.5)) == {}
    # waiting for this one when the late response of "slow" arrives
    response = await client.request(make_request("next", delay=0.8))

    assert response_id(response) == "next"


@pytest.mark.asyncio
async def test_async_requests_survive_socket_reset(server_addr):
    client = AsyncZMQClient("async_reset", server_addr)

    async def one(i):
        return i, await client.request(make_request(i, delay=0.2))

    in_flight = asyncio.gather(*(one(i) for i in range(20)))
    await asyncio.sleep(0.05)
    client.reset()
    before = await in_flight
    after = await asyncio.gather(*(one(i) for i in range(20, 40)))

    # requests sent before the reset may be lost, but never get another one's response
    assert all(response_id(resp) in (i, None) for i, resp in before)
    assert [(i, response_id(resp)) for i, resp in after] == [(i, i) for i in range(20, 40)]


@pytest.mark.asyncio
async def test_async_requests_mixed_with_sends(server_addr):
    client = AsyncZMQClient("async_mixed", server_addr)

    async def one(i):
        await client.send(make_request(f"msg_{i}", response_required=False))
        return i, await client.request(make_request(i, delay=random.uniform(0, 0.05)))

    results = await asyncio.gather(*(one(i) for i in range(100)))

    assert [(i, response_id(resp)) for i, resp in results] == [(i, i) for i in range(100)]


def test_sync_concurrent_threads_get_own_response(server_addr):
    client = ZMQClient("sync_concurrent", server_addr)

    def one(i):
        # fire-and-forget messages on the same socket must not break the request lock
        client.send(make_request(f"msg_{i}", response_required=False), use_lock=True)
        return i, client.request(make_request(i, delay=random.uniform(0, 0.01)))

    with ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(one, range(100)))

    assert [(i, response_id(resp)) for i, resp in results] == [(i, i) for i in range(100)]


def test_sync_late_response_is_not_returned_to_next_request(server_addr):
    client = ZMQClient("sync_late", server_addr)

    assert client.request(make_request("slow", delay=1.5)) == {}
    response = client.request(make_request("next", delay=0.8))

    assert response_id(response) == "next"
