from pydantic import BaseModel
from movai_core_shared.messages.general_data import Request


class LogTags(BaseModel):
    robot: str
    level: str
    service: str
    runtime: bool = False


class LogFields(BaseModel):
    module: str
    funcName: str
    lineno: int
    message: str


class LogData(BaseModel):
    measurement: str
    log_tags: LogTags
    log_fields: LogFields


class SyslogTags(BaseModel):
    appname: str
    facility: str
    host: str
    hostname: str
    severity: str


class SyslogFields(BaseModel):
    module: str
    funcName: str
    lineno: int
    facility_code: int
    message: str
    procid: int
    severity_code: int
    timestamp: int
    version: str


class SyslogData(BaseModel):
    measurement: str
    log_tags: SyslogTags
    log_fields: SyslogFields


class LogRequest(Request):
    req_data: LogData

    def get_client_log_format(self) -> dict:
        """Returns a dict with the format used to send to frontend.

        Returns:
            dict: A dictionary with the required fields.
        """
        log_msg = {
            "time": self.created,
            "robot": self.robot_info.robot,
            "service": self.robot_info.service,
            "module": self.req_data.log_fields.module,
            "lineno": self.req_data.log_fields.lineno,
            "funcName": self.req_data.log_fields.funcName,
            "level": self.req_data.log_tags.level,
            "message": self.req_data.log_fields.message,
        }
        return log_msg


class SyslogRequest(Request):
    req_data: SyslogData
