import os
import subprocess
import sys
import time

import pytest
import zmq

# A process that sends a message and exits right away, like a GD node after a transition
SENDER = """
import sys
from movai_core_shared.core.zmq.zmq_manager import ZMQManager, ZMQType

addr, flush, linger_ms = sys.argv[1], sys.argv[2] == "flush", int(sys.argv[3])
ZMQManager.get_client(addr, ZMQType.CLIENT).send({"msg": "last words"})
if flush:
    ZMQManager.shutdown(linger_ms)
"""

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def start_sender(addr: str, flush: bool, linger_ms: int = 5000) -> subprocess.Popen:
    env = dict(os.environ, PYTHONPATH=REPO_ROOT)
    args = [sys.executable, "-c", SENDER, addr, "flush" if flush else "no_flush", str(linger_ms)]
    return subprocess.Popen(args, env=env)


def receive(addr: str, sender: subprocess.Popen, wait_s: float) -> list:
    """Binds the server only after the sender sent its message, as if it was unresponsive."""
    time.sleep(wait_s)
    ctx = zmq.Context()
    router = ctx.socket(zmq.ROUTER)
    router.bind(addr)
    try:
        sender.wait(timeout=10)
        if router.poll(1000):
            return [router.recv_multipart()]
        return []
    finally:
        ctx.destroy(linger=0)


@pytest.fixture
def addr(tmp_path):
    return f"ipc://{tmp_path}/server.sock"


class TestZMQManagerShutdown:
    def test_message_lost_without_shutdown(self, addr):
        sender = start_sender(addr, flush=False)
        assert receive(addr, sender, wait_s=1) == []

    def test_shutdown_sends_queued_message(self, addr):
        sender = start_sender(addr, flush=True)
        messages = receive(addr, sender, wait_s=1)
        assert len(messages) == 1
        assert b"last words" in messages[0][-1]
        assert sender.returncode == 0

    def test_shutdown_waits_at_most_linger(self, addr):
        start = time.time()
        sender = start_sender(addr, flush=True, linger_ms=300)
        sender.wait(timeout=10)
        # nobody ever listens: the message is dropped once the linger elapses
        assert sender.returncode == 0
        assert time.time() - start < 5
