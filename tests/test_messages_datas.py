""" Test Messages Data classes """

import pytest
from movai_core_shared.messages import NotificationDataFactory
from movai_core_shared.messages.metric_data import MetricData
from movai_core_shared.messages.general_data import Request
from movai_core_shared.messages.log_data import (
    LogData,
    LogRequest,
    LogTags,
    LogFields,
    SyslogTags,
    SyslogFields,
    SyslogData,
)
from movai_core_shared.messages.command_data import CommandData, Command, CommandReq
from movai_core_shared.messages.stress_data import StressData, StressRequest


@pytest.mark.test_zmq
@pytest.mark.test_zmq_messages_data
class TestMessagesData:
    def test_notification_data(self):
        notification_data = NotificationDataFactory()
        assert notification_data is not None

    def test_metric_data(self):
        metric_data = MetricData(measurement="test", metric_type="test")
        assert metric_data is not None

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

    def test_log_data(self):
        log_data = LogData(
            measurement="test",
            log_tags=LogTags(robot="test", level="test", service="test", runtime=True),
            log_fields=LogFields(module="test", funcName="test", lineno=123, message="test"),
        )
        assert log_data is not None

    def test_syslog_tags(self):
        syslog_tags = SyslogTags(
            appname="test", facility="test", host="test", hostname="test", severity="test"
        )
        assert syslog_tags is not None

    def test_syslog_fields(self):
        syslog_fields = SyslogFields(
            module="test",
            funcName="test",
            lineno=123,
            facility_code=123,
            message="test",
            procid=123,
            severity_code=123,
            timestamp=123,
            version="test",
        )
        assert syslog_fields is not None

    def test_syslog_data(self):
        syslog_data = SyslogData(
            measurement="test",
            log_tags=SyslogTags(
                appname="test", facility="test", host="test", hostname="test", severity="test"
            ),
            log_fields=SyslogFields(
                module="test",
                funcName="test",
                lineno=123,
                facility_code=123,
                message="test",
                procid=123,
                severity_code=123,
                timestamp=123,
                version="test",
            ),
        )
        assert syslog_data is not None

    def test_log_request(self):
        log_request = LogRequest(
            req_type="test",
            created=123456,
            response_required=True,
            robot_info={"fleet": "test", "robot": "test", "service": "test", "id": "test"},
            req_data=LogData(
                measurement="test",
                log_tags=LogTags(robot="test", level="test", service="test", runtime=True),
                log_fields=LogFields(module="test", funcName="test", lineno=123, message="test"),
            ),
        )
        assert log_request is not None

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

    def test_stress_data(self):
        stress_data = StressData(
            current=123, total=123, insert=True, query=True, measurement="test"
        )
        assert stress_data is not None

    def test_stress_request(self):
        stress_request = StressRequest(
            req_type="test",
            created=123456,
            response_required=True,
            robot_info={"fleet": "test", "robot": "test", "service": "test", "id": "test"},
            req_data=StressData(
                current=123, total=123, insert=True, query=True, measurement="test"
            ),
        )
        assert stress_request is not None
