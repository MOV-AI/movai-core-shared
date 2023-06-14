import unittest
import asyncio

from movai_core_shared.logger import Log
from movai_core_shared.core.message_client import MessageClient

LOGGER = Log.get_logger(__name__)
TEST_SERVER_ADDR = "tcp://0.0.0.0:30000"
        

async def test_with_reponse():
    try:
        client = MessageClient(TEST_SERVER_ADDR, "test")
        data = {
            "msg": "Hello from client"
        }
        response = await client.send_request("test", data, None, True)
        LOGGER.info(response)
        if response.get("response") is None:
            raise ValueError("The field 'reponse' is missing")
        if response["response"].get("status") != "ok":
                raise ValueError("The status field is different than expected")
        if response.get("extra_data") is None:
            raise ValueError("The field 'extra_data' is missing")
        if response.get("extra_data") != "Hello from server":
            raise ValueError("The field 'extra_data' field is different than expected")
        LOGGER.info("test_with_reponse has completed")
    except Exception as err:
        LOGGER.error(err)
        
if __name__ == "__main__":
    asyncio.run(test_with_reponse())
