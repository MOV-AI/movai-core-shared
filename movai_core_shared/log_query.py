from typing import List, Optional, Union

import requests

from movai_core_shared.consts import (
    DEFAULT_LOG_LIMIT,
)
from movai_core_shared.messages.metric_data import LogQueryResponse
from movai_core_shared.common.time import validate_time
from movai_core_shared.logger import Log
from .base_query import BaseQuery

LOGGER = Log.get_logger(__name__)

# pylint: disable=too-many-arguments,too-many-locals,too-many-branches,invalid-name


class LogsQuery(BaseQuery):
    """A class for querying logs"""

    @classmethod
    async def get_logs(
        cls,
        limit=DEFAULT_LOG_LIMIT,
        robots=None,
        services=None,
        level=None,
        message=None,
        fromDate=None,
        toDate=None,
        tags: Optional[Union[List[str], str]] = None,
    ) -> LogQueryResponse:
        params = {}
        query = {}
        query_parts = ["logfmt"]

        if limit is not None:
            params["limit"] = cls.validate_value("limit", limit)
            if params["limit"] > 300:
                params["limit"] = 300

        if robots is not None:
            query["robot"] = robots

        if level is not None:
            query_parts.append(f'detected_level="{level.upper()}"')

        if message is not None:
            msg = cls.validate_message(message)
            query_parts.append(f'~"(?i){msg}"')

        if fromDate is not None:
            params["start"] = int(validate_time(fromDate) * 1e9)

        if toDate is not None:
            params["end"] = int(validate_time(toDate) * 1e9)

        if services is not None:
            query["service_name"] = services

        if tags is not None:
            if isinstance(tags, str):
                tags = [tags]
            query_parts.append("|".join([f'tags="{tag}:True"' for tag in tags]))

        params["query"] = "{" + ", ".join(f'{k}="{v}"' for k, v in query.items()) + "}"

        if query_parts:
            params["query"] += "|" + "|".join(query_parts)

        LOGGER.info(f"Querying Loki with params: {params}")

        response = requests.get("http://loki:3100/loki/api/v1/query_range", params=params)
        response.raise_for_status()

        LOGGER.info(f"Loki response: {response.json()}")

        compatible_data = []

        data = response.json().get("data", {}).get("result", [])

        for msg in data:
            compatible_data.append(
                {
                    "robot": msg["stream"]["robot"],
                    "level": msg["stream"]["detected_level"],
                    "service": msg["stream"]["service"],
                    "runtime": False,
                    "module": "<string>",
                    "funcName": "<module>",
                    "lineno": 1,
                    "message": msg["stream"]["message"],
                    "args": None,
                    "time": int(msg["values"][0][0]) // 1_000_000_000,
                    "ui": "True",
                }
            )

        compatible_data.reverse()

        compatible_response = {
            "success": True,
            "results": {
                "limit": limit,
                "offset": 0,
                "count": len(response.json().get("data", {}).get("result", [])),
                "data": compatible_data,
            },
        }

        LOGGER.info(f"Loki compatible response: {compatible_response}")

        return LogQueryResponse(**compatible_response)
