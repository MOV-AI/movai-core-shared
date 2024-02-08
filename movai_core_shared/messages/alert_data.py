"""
   Copyright (C) Mov.ai  - All Rights Reserved
   Unauthorized copying of this file, via any medium is strictly prohibited
   Proprietary and confidential

   Developers:
   - Erez Zomer (erez@mov.ai) - 2023
"""
from pydantic import BaseModel

from movai_core_shared.messages.general_data import Request
from movai_core_shared.messages.metric_data import MetricData


class Alert(BaseModel):
    name: str
    info: str
    action: str
    callback: str
    status: str
    send_email: bool = False


class AlertData(MetricData):
    metric_fields: Alert


class AlertRequest(Request):
    req_data: AlertData
