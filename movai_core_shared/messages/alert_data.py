from pydantic import BaseModel

from movai_core_shared.messages.general_data import Request


class MetricData(BaseModel):
    name: str
    info: str
    action: str
    callback: str
    status: str
    send_email: bool = False


class AlertData(BaseModel):
    measurement: str
    metric_type: str
    metric_data: MetricData


class AlertRequest(Request):
    req_data: AlertData

