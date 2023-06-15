import unittest
from pydantic import BaseModel
from multiprocessing import Process
from movai_core_shared.logger import Log
from movai_core_shared.core.zmq_client import ZMQClient
from movai_core_shared.core.zmq_server import ZMQServer
from movai_core_shared.core.message_client import MessageClient
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
        response = {
                "status": "ok"
        }
        return response

    async def handle_response(self, response):
        response["extra_data"] = "Hello from server"
        self.stop()
        return response


def create_test_server():
    server = TestServer()
    server.run()
        

class TestZMQ(unittest.TestCase):
    
    @classmethod
    def setUpClass(self):
        self.client = MessageClient(TEST_SERVER_ADDR)
        self.data = {
            "msg": "Hello from client"
        }

    def test_with_reponse(self):
        try:
            p = Process(target=create_test_server)
            p.start()
            response = self.client.send_request("test", self.data, None, True)
            p.kill()
            LOGGER.info(response)
            self.assertFalse(response.get("response") is None)
            self.assertTrue(response["response"].get("status") == "ok")
            self.assertFalse(response.get("extra_data") is None)
            self.assertTrue(response.get("extra_data") == "Hello from server")
        except Exception as exc:
            LOGGER.error(exc)
            p.kill()

        
if __name__ == "__main__":
    unittest.main()
