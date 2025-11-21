"""
   Copyright (C) Mov.ai  - All Rights Reserved
   Unauthorized copying of this file, via any medium is strictly prohibited
   Proprietary and confidential

   Developers:
   - Erez Zomer (erez@mov.ai) - 2023
"""
from typing import Union, Literal, Optional

from pydantic import BaseModel

from movai_core_shared.consts import DeactivationType


class AlertActivationData(BaseModel):
    args: Optional[str]
    activation_date: str


class AlertDeactivationData(BaseModel):
    deactivation_date: str
    deactivation_type: Union[
        Literal[DeactivationType.REQUESTED], Literal[DeactivationType.AUTO_CLEARED]
    ]


class AlertData(AlertActivationData, AlertDeactivationData):
    alert_id: str
