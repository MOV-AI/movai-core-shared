"""Copyright (C) Mov.ai  - All Rights Reserved
Unauthorized copying of this file, via any medium is strictly prohibited
Proprietary and confidential

Developers:
- Erez Zomer (erez@mov.ai) - 2023

"""
from typing import List
from pydantic import BaseModel

from movai_core_shared.messages.log_data import LogFields, LogTags


class LogQueryContent(LogFields, LogTags):
    time: int


class LogQueryData(BaseModel):
    limit: int
    offset: int
    count: int
    data: List[LogQueryContent]


class AlertQueryContent(BaseModel):
    time: int
    activation_date: str
    alert_id: str
    args: str
    deactivation_date: str
    deactivation_type: str
    fleet: str
    id: str
    robot: str
    service: str


class AlertQueryData(BaseModel):
    limit: int
    offset: int
    count: int
    data: List[AlertQueryContent]
