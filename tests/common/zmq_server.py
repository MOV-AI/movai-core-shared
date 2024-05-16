import json

from typing import Optional
from pydantic import BaseModel
from movai_core_shared.logger import Log
from movai_core_shared.core.zmq.zmq_server import ZMQServer
from movai_core_shared.messages.general_data import Request

TEST_SERVER_ADDR = "ipc:///tmp/test_zmq_server"


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
        index = len(buffer) - 1
        data = buffer[index]

        if data is None:
            self.log.error(f"{self._name} No data received")
            return

        self.log.debug(f"{self._name} received data {data}")

        request = json.loads(data)
        response = self.handle_request(request)
        response_required = request.get("response_required", False)
        if response_required:
            self.log.debug(f"{self._name} sending response {response}")
            response = self.handle_response(response)
            await self._socket.send_multipart([json.dumps(response).encode()])
        else:
            self.log.debug(f"{self._name} no response required")

    def handle_request(self, request):
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


def create_test_server():
    server = TestServer()
    server.run()


if __name__ == "__main__":
    create_test_server()
