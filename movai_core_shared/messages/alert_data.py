"""
   Copyright (C) Mov.ai  - All Rights Reserved
   Unauthorized copying of this file, via any medium is strictly prohibited
   Proprietary and confidential

   Developers:
   - Erez Zomer (erez@mov.ai) - 2023
"""
from typing import Union, Literal

from pydantic import BaseModel

from movai_core_shared.consts import DeactivationType
from movai_core_shared.messages.general_data import Request
from movai_core_shared.messages.metric_data import MetricData


class Alert(BaseModel):
    name: str
    info: str
    action: str
    callback: str
    status: str
    send_email: bool = False


class OldAlertData(MetricData):
    metric_fields: Alert


class AlertRequest(Request):
    req_data: OldAlertData


class AlertActivationData(BaseModel):
    args: str
    activation_date: str


class AlertDeactivationData(BaseModel):
    deactivation_date: str
    deactivation_type: Union[
        Literal[DeactivationType.REQUESTED], Literal[DeactivationType.AUTO_CLEARED]
    ]


class AlertData(AlertActivationData, AlertDeactivationData):
    alert_id: str
