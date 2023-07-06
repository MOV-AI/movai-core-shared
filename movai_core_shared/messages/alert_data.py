from pydantic import BaseModel

from movai_core_shared.messages.general_data import Request
from movai_core_shared.messages.metric_data import MetricData




class AlertFields(BaseModel):
    name: str
    info: str
    action: str
    callback: str
    status: str
    send_email: bool = False


class AlertData(MetricData):
    measurement: str
    metric_type: str
    metric_fields: AlertFields


class AlertRequest(Request):
    req_data: AlertData

