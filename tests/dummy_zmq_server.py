import unittest
from pydantic import BaseModel
from movai_core_shared.logger import Log
from movai_core_shared.core.zmq.zmq_server import ZMQServer
from movai_core_shared.messages.general_data import Request

LOGGER = Log.get_logger(__name__)
TEST_SERVER_ADDR = "tcp://0.0.0.0:30000"


class SimpleData(BaseModel):
    msg: str


class SimpleRequest(Request):
    req_data: SimpleData


class TestServer(ZMQServer):
    def __init__(self) -> None:
        super().__init__("TEST_SERVER", TEST_SERVER_ADDR, True, True)

    async def handle_request(self, request: dict):
        LOGGER.debug(f"{self._name} handling request")
        LOGGER.debug(request)
        request = SimpleRequest(**request)
        LOGGER.info(request.req_data.msg)
        response = {"status": "ok"}
        return response

    async def handle_response(self, response):
        response["extra_data"] = "Hello from server"
        return response


def create_test_server():
    server = TestServer()
    server.run()


if __name__ == "__main__":
    create_test_server()
