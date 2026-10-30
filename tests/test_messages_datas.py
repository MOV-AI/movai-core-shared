""" Test Messages Data classes """

import pytest
from movai_core_shared.messages.notification_data import NotificationDataFactory
from movai_core_shared.messages.general_data import Request
from movai_core_shared.messages.log_data import (
    LogTags,
    LogFields,
)
from movai_core_shared.messages.command_data import CommandData, Command, CommandReq


@pytest.mark.test_zmq
@pytest.mark.test_zmq_messages_data
class TestMessagesData:
    def test_notification_data(self):
        notification_data = NotificationDataFactory()
        assert notification_data is not None

    def test_request(self):
        request = Request(
            req_type="test",
            created=123456,
            response_required=True,
            robot_info={"fleet": "test", "robot": "test", "service": "test", "id": "test"},
        )
        assert request is not None

    def test_log_tags(self):
        log_tags = LogTags(robot="test", level="test", service="test", runtime=True)
        assert log_tags is not None

    def test_log_fields(self):
        log_fields = LogFields(module="test", funcName="test", lineno=123, message="test")
        assert log_fields is not None

    def test_command_data(self):
        command_data = CommandData(
            command="test", flow="test", node="test", port="test", data={"test": "test"}
        )
        assert command_data is not None

    def test_command(self):
        command = Command(
            command_data=CommandData(
                command="test", flow="test", node="test", port="test", data={"test": "test"}
            ),
            dst={"ip": "test", "host": "test", "id": "test"},
        )
        assert command is not None

    def test_command_req(self):
        command_req = CommandReq(
            req_type="test",
            created=123456,
            response_required=True,
            robot_info={"fleet": "test", "robot": "test", "service": "test", "id": "test"},
            req_data=Command(
                command_data=CommandData(
                    command="test", flow="test", node="test", port="test", data={"test": "test"}
                ),
                dst={"ip": "test", "host": "test", "id": "test"},
            ),
        )
        assert command_req is not None
