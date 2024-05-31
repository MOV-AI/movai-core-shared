""" Test MessageClient class """

import pytest
import zmq
from movai_core_shared.core.zmq.zmq_manager import ZMQManager, ZMQType
from unittest.mock import patch, MagicMock
from movai_core_shared.core.message_client import MessageClient, AsyncMessageClient
from movai_core_shared.envvars import FLEET_NAME, DEVICE_NAME, SERVICE_NAME
from movai_core_shared.exceptions import ArgumentError, MessageFormatError

@pytest.mark.test_zmq
@pytest.mark.test_zmq_message_client
class TestZMQMessageClient:
    def test_message_client_init(self):
        server_addr = "tcp://localhost:5555"
        with pytest.raises(TypeError):
            MessageClient(server_addr=123)
        with pytest.raises(ArgumentError):
            MessageClient(server_addr="")
        with patch("movai_core_shared.core.message_client.ZMQManager.get_client") as mock_get_client:
            MessageClient(server_addr=server_addr)
            mock_get_client.assert_called_once_with(server_addr, ZMQType.CLIENT)

    def test_message_client_build_request(self):
        server_addr = "tcp://localhost:5555"
        msg_type = "logs"
        data = {"key": "value"}

        message_client = MessageClient(server_addr=server_addr)
        request = message_client._build_request(msg_type=msg_type, data=data)["request"]
        assert request["req_type"] == msg_type
        assert request["req_data"] == data
        assert request["response_required"] == False
        assert request["created"] is not None
        assert request["robot_info"]["robot"] == DEVICE_NAME
        assert request["robot_info"]["fleet"] == FLEET_NAME
        assert request["robot_info"]["service"] == SERVICE_NAME
        assert request["robot_info"]["id"] == ""

    def test_message_client_build_request_with_robot_id(self):
        server_addr = "tcp://localhost:5555"
        msg_type = "logs"
        data = {"key": "value"}
        robot_id = "robot_id"

        message_client = MessageClient(server_addr=server_addr, robot_id=robot_id)
        request = message_client._build_request(msg_type=msg_type, data=data)["request"]
        assert request["req_type"] == msg_type
        assert request["req_data"] == data
        assert request["response_required"] == False
        assert request["created"] is not None
        assert request["robot_info"]["robot"] == DEVICE_NAME
        assert request["robot_info"]["fleet"] == FLEET_NAME
        assert request["robot_info"]["service"] == SERVICE_NAME
        assert request["robot_info"]["id"] == robot_id

    def test_message_client_build_request_with_response_required(self):
        server_addr = "tcp://localhost:5555"
        msg_type = "logs"
        data = {"key": "value"}

        message_client = MessageClient(server_addr=server_addr)
        request = message_client._build_request(msg_type=msg_type, data=data, response_required=True)["request"]
        assert request["req_type"] == msg_type
        assert request["req_data"] == data
        assert request["response_required"] == True
        assert request["created"] is not None
        assert request["robot_info"]["robot"] == DEVICE_NAME
        assert request["robot_info"]["fleet"] == FLEET_NAME
        assert request["robot_info"]["service"] == SERVICE_NAME
        assert request["robot_info"]["id"] == ""

    def test_message_client_fetch_response(self):
        server_addr = "tcp://localhost:5555"
        msg_type = "logs"
        data = {"key": "value"}

        message_client = MessageClient(server_addr=server_addr)
        request = message_client._build_request(msg_type=msg_type, data=data)
        response = message_client._fetch_response(request)
        assert response["response"]["request"] == request["request"]

    def test_message_client_fetch_response_with_invalid_msg(self):
        server_addr = "tcp://localhost:5555"
        message_client = MessageClient(server_addr=server_addr)
        with pytest.raises(MessageFormatError):
            message_client._fetch_response("invalid_msg")

    def test_message_client_send_request(self):
        server_addr = "tcp://localhost:5555"
        msg_type = "logs"
        data = {"key": "value"}
        message_client = MessageClient(server_addr=server_addr)
        message_client.send_request(msg_type=msg_type, data=data)

    def test_message_client_send_request_with_response_required(self):
        server_addr = "tcp://localhost:5555"
        msg_type = "logs"
        data = {"key": "value"}
        message_client = MessageClient(server_addr=server_addr)
        message_client.send_request(msg_type=msg_type, data=data, response_required=True)

    def test_message_client_forward_request_msg(self):
        server_addr = "tcp://localhost:5555"
        msg_type = "logs"
        data = {"key": "value"}
        message_client = MessageClient(server_addr=server_addr)
        message_client.forward_request(request_msg={"request": {"req_type": msg_type, "req_data": data}})

    def test_message_client_forward_request_msg_without_request(self):
        server_addr = "tcp://localhost:5555"
        msg_type = "logs"
        data = {"key": "value"}
        message_client = MessageClient(server_addr=server_addr)
        message_client.forward_request(request_msg={"req_type": msg_type, "req_data": data})

    def test_message_client_forward_request_msg_with_response_required(self):
        server_addr = "tcp://localhost:5555"
        msg_type = "logs"
        data = {"key": "value"}
        message_client = MessageClient(server_addr=server_addr)
        message_client.forward_request(request_msg={"request": {"req_type": msg_type, "req_data": data, "response_required": True}})

    def test_message_client_send_msg(self):
        server_addr = "tcp://localhost:5555"
        msg = {"key": "value"}
        message_client = MessageClient(server_addr=server_addr)
        message_client.send_msg(msg)

    def test_message_client_send_msg_with_data(self):
        server_addr = "tcp://localhost:5555"
        msg = {"key": "value"}
        extra_data = {"data": "extra_data"}
        message_client = MessageClient(server_addr=server_addr)
        message_client.send_msg(msg, extra_data=extra_data)

@pytest.mark.test_zmq
@pytest.mark.test_zmq_message_client
class TestZMQAsyncMessageClient:
    def test_async_message_client_init(self):
        server_addr = "tcp://localhost:5555"
        with pytest.raises(TypeError):
            AsyncMessageClient(server_addr=123)
        with pytest.raises(ArgumentError):
            AsyncMessageClient(server_addr="")
        with patch("movai_core_shared.core.message_client.ZMQManager.get_client") as mock_get_client:
            AsyncMessageClient(server_addr=server_addr)
            mock_get_client.assert_called_once_with(server_addr, ZMQType.ASYNC_CLIENT)

    def test_async_message_client_build_request(self):
        server_addr = "tcp://localhost:5555"
        msg_type = "logs"
        data = {"key": "value"}

        message_client = AsyncMessageClient(server_addr=server_addr)
        request = message_client._build_request(msg_type=msg_type, data=data)["request"]
        assert request["req_type"] == msg_type
        assert request["req_data"] == data
        assert request["response_required"] == False
        assert request["created"] is not None
        assert request["robot_info"]["robot"] == DEVICE_NAME
        assert request["robot_info"]["fleet"] == FLEET_NAME
        assert request["robot_info"]["service"] == SERVICE_NAME
        assert request["robot_info"]["id"] == ""

    @pytest.mark.asyncio
    async def test_async_message_client_send_request(self):
        server_addr = "tcp://localhost:5555"
        msg_type = "logs"
        data = {"key": "value"}
        message_client = AsyncMessageClient(server_addr=server_addr)
        await message_client.send_request(msg_type=msg_type, data=data)

    @pytest.mark.asyncio
    async def test_async_message_client_send_request_with_response_required(self):
        server_addr = "tcp://localhost:5555"
        msg_type = "logs"
        data = {"key": "value"}
        message_client = AsyncMessageClient(server_addr=server_addr)
        await message_client.send_request(msg_type=msg_type, data=data, response_required=True)

    @pytest.mark.asyncio
    async def test_async_message_client_forward_request_msg(self):
        server_addr = "tcp://localhost:5555"
        msg_type = "logs"
        data = {"key": "value"}
        message_client = AsyncMessageClient(server_addr=server_addr)
        await message_client.forward_request(request_msg={"request": {"req_type": msg_type, "req_data": data, "response_required": False}})

    @pytest.mark.asyncio
    async def test_async_message_client_forward_request_msg_without_request(self):
        server_addr = "tcp://localhost:5555"
        msg_type = "logs"
        data = {"key": "value"}
        message_client = AsyncMessageClient(server_addr=server_addr)
        await message_client.forward_request(request_msg={"req_type": msg_type, "req_data": data, "response_required": False})

    @pytest.mark.asyncio
    async def test_async_message_client_forward_request_msg_with_response_required(self):
        server_addr = "tcp://localhost:5555"
        msg_type = "logs"
        data = {"key": "value"}
        message_client = AsyncMessageClient(server_addr=server_addr)
        await message_client.forward_request(request_msg={"request": {"req_type": msg_type, "req_data": data, "response_required": True}})

    @pytest.mark.asyncio
    async def test_async_message_client_send_msg(self):
        server_addr = "tcp://localhost:5555"
        msg = {"key": "value"}
        message_client = AsyncMessageClient(server_addr=server_addr)
        await message_client.send_msg(msg)

    @pytest.mark.asyncio
    async def test_async_message_client_send_msg_with_data(self):
        server_addr = "tcp://localhost:5555"
        msg = {"key": "value"}
        extra_data = {"data": "extra_data"}
        message_client = AsyncMessageClient(server_addr=server_addr)
        await message_client.send_msg(msg, extra_data=extra_data)

