import pytest
import zmq

from movai_core_shared.core.zmq.zmq_client import ZMQClient
from movai_core_shared.core.zmq.zmq_helpers import generate_zmq_identity


@pytest.fixture
def router(tmp_path):
    ctx = zmq.Context()
    socket = ctx.socket(zmq.ROUTER)
    addr = f"ipc://{tmp_path}/server.sock"
    socket.bind(addr)
    yield socket, addr
    ctx.destroy(linger=0)


def received(router: zmq.Socket, timeout_ms: int = 1000) -> list:
    messages = []
    while router.poll(timeout_ms):
        messages.append(router.recv_multipart())
        timeout_ms = 100
    return messages


class TestZMQIdentity:
    def test_identities_are_unique(self):
        identities = {generate_zmq_identity("dealer") for _ in range(10000)}
        assert len(identities) == 10000
        assert all("_dealer_" in identity for identity in identities)

    def test_reset_changes_identity(self, router):
        _, addr = router
        client = ZMQClient("TEST_CLIENT", addr)
        assert client._identity == b"TEST_CLIENT"

        client.reset()
        first_reset = client._identity
        client.reset(force=True)

        assert first_reset.startswith(b"TEST_CLIENT_")
        assert client._identity.startswith(b"TEST_CLIENT_")
        assert client._identity != first_reset

    def test_server_ignores_duplicated_identity(self, router):
        socket, addr = router
        live_client = ZMQClient("TEST_CLIENT", addr)
        live_client.send({"msg": "live"})
        assert len(received(socket)) == 1

        # like a reset socket while the previous one, with the same identity, is still connected
        duplicated_client = ZMQClient("TEST_CLIENT", addr)
        duplicated_client.send({"msg": "duplicated"})
        assert received(socket) == []

    def test_message_after_reset_is_received(self, router):
        socket, addr = router
        live_client = ZMQClient("TEST_CLIENT", addr)
        live_client.send({"msg": "live"})
        assert len(received(socket)) == 1

        reset_client = ZMQClient("TEST_CLIENT", addr)
        reset_client.reset()
        reset_client.send({"msg": "after reset"})

        messages = received(socket)
        assert len(messages) == 1
        assert messages[0][0] == reset_client._identity
        assert b"after reset" in messages[0][-1]
