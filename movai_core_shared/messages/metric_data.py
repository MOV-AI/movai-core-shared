"""Copyright (C) Mov.ai  - All Rights Reserved
Unauthorized copying of this file, via any medium is strictly prohibited
Proprietary and confidential

Developers:
- Erez Zomer (erez@mov.ai) - 2023

"""
from typing import Literal
from typing import Optional

from movai_core_shared.consts import LOGS_INFLUX_DB
from movai_core_shared.consts import METRICS_INFLUX_DB
from movai_core_shared.consts import PLATFORM_METRICS_INFLUX_DB
from movai_core_shared.messages.general_data import Request
from pydantic import BaseModel


class MetricData(BaseModel):
    """Metrics data.

    Attributes:
        measurement (str): The name of the measurement.
        db_name (Literal[METRICS_INFLUX_DB, PLATFORM_METRICS_INFLUX_DB]): The database name.
        metric_fields (Optional[dict]): Measurement fields.
        metric_tags (Optional[dict]): Measurement tags.

    """

    measurement: str
    db_name: Literal[
        Literal[METRICS_INFLUX_DB], Literal[PLATFORM_METRICS_INFLUX_DB]
    ] = METRICS_INFLUX_DB
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
    count_field: Optional[str] = None
    db_name: Literal[
        Literal[LOGS_INFLUX_DB], Literal[METRICS_INFLUX_DB], Literal[PLATFORM_METRICS_INFLUX_DB]
    ] = None


class MetricQueryRequest(Request):
    req_data: MetricQueryData


class MetricQueryResponse(BaseModel):
    """Respone for MetricQueryRequest.

    Attributes:
        success (bool): Indicates if the query was successful.
        results (dict): The results of the query.
        error (Optional[str]): Error message if the query failed.
        reason (Optional[str]): Reason for failure, if applicable.

    """

    success: bool
    results: dict
    error: Optional[str] = None
    reason: Optional[str] = None
