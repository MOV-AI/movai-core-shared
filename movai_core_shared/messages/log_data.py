from pydantic import BaseModel
from movai_core_shared.messages.general_data import Request

# {'req_type': 'logs',
# 'created': 1679400413494329237,
# 'response_required': False,
# 'req_data': {
#     'measurement': 'app_logs',
#     'log_tags': {
#         'robot_name': 'dev-manager-2-4-1',
#         'level': 'INFO',
#         'service': 'backend'
#         },
#     'log_fields': {
#         'module': 'web_log',
#         'funcName': 'log',
#         'lineno': 206,
#         'message': '172.31.0.2 [21/Mar/2023:12:06:53 +0000] "POST /token-verify/ HTTP/1.1" 400 207 "https://192.168.1.10/api/v1/apps/mov-fe-app-taskmanager/dashboard/task_templates/test1/" "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"'
#         }
#     },
# 'robot_info': {
#     'fleet': 'movai',
#     'robot': 'dev-manager-2-4-1',
#     'service': 'backend',
#     'id': ''
#     }
# }


class LogTags(BaseModel):
    robot: str
    level: str
    service: str
    runtime: bool = False

    def __str__(self) -> str:
        text = f"""
                robot: {self.robot}
                level: {self.level}
                service: {self.service}
                runtime: {self.runtime}"""
        return text


class LogFields(BaseModel):
    module: str
    funcName: str
    lineno: int
    message: str

    def __str__(self) -> str:
        text = f"""
                module: {self.module}
                funcName: {self.funcName}
                lineno: {self.lineno}
                message: {str(self.message)}"""
        return text


class LogData(BaseModel):
    measurement: str
    log_tags: LogTags
    log_fields: LogFields

    def __str__(self) -> str:
        text = f"""
            measurement: {self.measurement}
            log_tags: {self.log_tags.__str__()}
            log_fields: {self.log_fields.__str__()}"""
        return text


class SyslogTags(BaseModel):
    appname: str
    facility: str
    host: str
    hostname: str
    severity: str

    def __str__(self) -> str:
        text = f"""
                appname: {self.appname}
                facility: {self.facility}
                host: {self.host}
                hostname: {self.hostname}
                severity: {self.severity}
                """
        return text


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

    def __str__(self) -> str:
        text = f"""
                module: {self.module}
                funcName: {self.funcName}
                lineno: {self.lineno}
                facility_code: {self.facility_code}
                message: {str(self.message)}
                procid: {self.procid}
                severity_code: {self.severity_code}
                timestamp: {self.timestamp}
                version: {self.version}
                """
        return text


class SyslogData(BaseModel):
    measurement: str
    log_tags: SyslogTags
    log_fields: SyslogFields

    def __str__(self) -> str:
        text = f"""
            measurement: {self.measurement}
            log_tags: {self.log_tags.__str__()}
            log_fields: {self.log_fields.__str__()}"""
        return text


class LogRequest(Request):
    req_data: LogData

    def __str__(self):
        text = f"""
        ===========================================================================================
        req_type: {self.req_type}
        response_required: {self.response_required}
        req_data: {self.req_data.__str__()}
        robot_info: {self.robot_info.__str__()}
        created: {self.created}
        ==========================================================================================="""
        return text

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
            "message": self.req_data.log_fields.message
            }
        return log_msg

class SyslogRequest(Request):
    req_data: SyslogData

    def __str__(self):
        text = f"""
        ===========================================================================================
        req_type: {self.req_type}
        response_required: {self.response_required}
        req_data: {self.req_data.__str__()}
        robot_info: {self.robot_info.__str__()}
        created: {self.created}
        ==========================================================================================="""
        return text
