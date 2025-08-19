import asyncio
import json

from typing import Optional
from pydantic import BaseModel
from movai_core_shared.logger import Log
from movai_core_shared.core.zmq.zmq_server import ZMQServer
from movai_core_shared.messages.general_data import Request

TEST_SERVER_ADDR = "ipc:///tmp/test_zmq_server"
# TEST_SERVER_ADDR = "tcp://localhost:5555"


class SimpleData(BaseModel):
    msg: str


class SimpleRequest(Request):
    req_id: Optional[str] = None
    req_data: SimpleData
    req_type: str
    created: int
    response_required: bool


class TestServer(ZMQServer):
    def __init__(self, logger=None) -> None:
        super().__init__("TEST_SERVER", TEST_SERVER_ADDR, True)
        if logger is None:
            self.log = Log.get_logger(__name__)
        else:
            self.log = logger
        self.log.info("TestServer initialized")

    async def handle(self, buffer: bytes) -> None:
        """The main function to handle incoming requests by ZMQServer.
        Copied from flow_initiator/spawner/spawner_server.py

        Args:
            buffer (bytes): The buffer that the server was able to read.
        """
        response_msg = None
        try:
            index = len(buffer) - 1
            msg = buffer[index]
            if msg is None:
                self._logger.error("Got an empty msg!")
                return
            self._logger.debug("Got msg: %s", msg)
            request = json.loads(msg)
            request = request.get("request")
            req_data = request.get("req_data")

            asyncio.create_task(self.handle_request(req_data))
            response_msg = "Got request & successfully proccessed".encode("utf8")
        except json.JSONDecodeError as exc:
            self._logger.error("can't parse command: %s", buffer)
            self._logger.error(exc)
            response_msg = f"can't parse command: {buffer}".encode("utf8")
        finally:
            resp = {"status": response_msg}
            resp = json.dumps(resp).encode("utf8")
            await self._socket.send_multipart(resp)

    async def handle_request(self, request):
        self.log.debug(f"{self._name} handling request {request}")
        request = SimpleRequest(**request)
        if request.req_data.msg == "exit":
            self.stop()
            return {"status": "ok", "msg": "exiting"}
        elif request.req_data.msg == "raise":
            raise ValueError("raising exception")
        elif request.req_data.msg == "log":
            self.log.info(request.req_data.msg)

        response = {"status": "ok"}
        return response

    def handle_response(self, response):
        response["extra_data"] = "Hello from server"
        return response

    def stop(self):
        self.log.info("Stopping server")
        self._running = False
        self._socket.close()


def create_test_server():
    server = TestServer()
    server.run()


if __name__ == "__main__":
    create_test_server()
