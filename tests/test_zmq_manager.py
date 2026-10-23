import os
import subprocess
import sys
import time

import pytest
import zmq

# A process that sends a message and exits right away, like a GD node after a transition
SENDER = """
import atexit
import sys
import threading
import time
from movai_core_shared.core.zmq.zmq_manager import ZMQManager, ZMQType

addr, mode = sys.argv[1], sys.argv[2]
if mode.startswith("blocked_"):
    # another client waits for a message forever, holding its lock
    zmq_type = ZMQType.SUBSCRIBER if mode == "blocked_subscriber" else ZMQType.CLIENT
    idle = ZMQManager.get_client(addr + ".idle", zmq_type)
    threading.Thread(target=idle.receive, kwargs={"use_lock": True}, daemon=True).start()
    time.sleep(0.2)
ZMQManager.get_client(addr, ZMQType.CLIENT).send({"msg": "last words"})
if mode == "shutdown":
    ZMQManager.shutdown()
elif mode == "reset":
    ZMQManager.get_client(addr, ZMQType.CLIENT).reset()
elif mode == "no_atexit":
    atexit.unregister(ZMQManager.shutdown)
"""

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def start_sender(
    addr: str, mode: str = "exit", linger_ms: int = 5000, recv_timeout_ms: int = 2500
) -> subprocess.Popen:
    env = dict(
        os.environ,
        PYTHONPATH=REPO_ROOT,
        MOVAI_ZMQ_SHUTDOWN_LINGER_MS=str(linger_ms),
        MOVAI_ZMQ_RECV_TIMEOUT_MS=str(recv_timeout_ms),
    )
    return subprocess.Popen([sys.executable, "-c", SENDER, addr, mode], env=env)


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
    def test_message_lost_without_shutdown_at_exit(self, addr):
        sender = start_sender(addr, mode="no_atexit")
        assert receive(addr, sender, wait_s=1) == []

    def test_queued_message_sent_at_exit(self, addr):
        sender = start_sender(addr)
        messages = receive(addr, sender, wait_s=1)
        assert len(messages) == 1
        assert b"last words" in messages[0][-1]
        assert sender.returncode == 0

    def test_shutdown_sends_queued_message(self, addr):
        sender = start_sender(addr, mode="shutdown")
        messages = receive(addr, sender, wait_s=1)
        assert len(messages) == 1
        assert b"last words" in messages[0][-1]
        assert sender.returncode == 0

    def test_exit_waits_at_most_linger(self, addr):
        start = time.time()
        sender = start_sender(addr, linger_ms=300)
        sender.wait(timeout=10)
        # nobody ever listens: the message is dropped once the linger elapses
        assert sender.returncode == 0
        assert time.time() - start < 5

    def test_exit_after_reset_waits_at_most_linger(self, addr):
        start = time.time()
        # the socket closed by the reset still holds the message nobody receives
        sender = start_sender(addr, mode="reset", linger_ms=300)
        sender.wait(timeout=10)
        assert sender.returncode == 0
        assert time.time() - start < 5

    @pytest.mark.parametrize("mode", ["blocked_subscriber", "blocked_client"])
    def test_exit_with_blocked_receiver(self, addr, mode):
        start = time.time()
        sender = start_sender(addr, mode=mode, recv_timeout_ms=-1)
        messages = receive(addr, sender, wait_s=1)
        assert len(messages) == 1
        assert b"last words" in messages[0][-1]
        assert sender.returncode == 0
        assert time.time() - start < 5
