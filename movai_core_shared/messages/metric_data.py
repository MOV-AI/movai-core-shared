"""
   Copyright (C) Mov.ai  - All Rights Reserved
   Unauthorized copying of this file, via any medium is strictly prohibited
   Proprietary and confidential

   Developers:
   - Erez Zomer (erez@mov.ai) - 2023
"""
from typing import Optional

from pydantic import BaseModel

from movai_core_shared.messages.general_data import Request


class MetricData(BaseModel):
    measurement: str
    metric_type: str
    metric_fields: Optional[dict] = None
    metric_tags: Optional[dict] = None


class MetricRequest(Request):
    req_data: MetricData


class QueryData(BaseModel):
    limit: int
    offset: int
    tags: Optional[dict] = None
    robots: Optional[list] = None
    from_: Optional[int] = None
    to_: Optional[int] = None


class MetricQueryData(BaseModel):
    measurement: str
    query_data: QueryData


class MetricQueryRequest(Request):
    req_data: MetricQueryData
