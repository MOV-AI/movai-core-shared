"""Alert query."""
from typing import List, Union
from movai_core_shared.consts import (
    ALERT_QUERY_HANDLER_MSG_TYPE,
    DEFAULT_LOG_LIMIT,
    DEFAULT_LOG_OFFSET,
    LOGS_MEASUREMENT,
)
from movai_core_shared.envvars import (
    LOCAL_MESSAGE_SERVER,
    MASTER_MESSAGE_SERVER,
)
from movai_core_shared.messages.metric_data import AlertQueryResponse
from movai_core_shared.core.message_client import AsyncMessageClient
from movai_core_shared.common.utils import is_manager
from movai_core_shared.common.time import validate_time

from .base_query import BaseQuery

# pylint: disable=too-many-arguments


class AlertQuery(BaseQuery):
    """Queryies alerts."""

    @classmethod
    async def get_alerts(
        cls,
        limit: int = DEFAULT_LOG_LIMIT,
        offset: int = DEFAULT_LOG_OFFSET,
        robots: List[str] = None,
        from_date: Union[int, str] = None,
        to_date: Union[int, str] = None,
        order_by: str = None,
        order_dir: str = None,
    ) -> AlertQueryResponse:
        """Get alerts from message-server.

        Args:
            limit: Maximum number of measurements to return.
            offset: Query offset.
            robots: List of robot names to filter.
            from_date: Start date to filter.
            to_date: End date to filter.
            order_by: Field to order the measurements by.
            order_dir: Direction of ordering.

        Returns:
            AlertQueryResponse: The response containing the queried alerts.

        """
        server_addr = MASTER_MESSAGE_SERVER
        if is_manager():
            server_addr = LOCAL_MESSAGE_SERVER

        message_client = AsyncMessageClient(server_addr)
        params = {}

        if limit is not None:
            params["limit"] = cls.validate_value("limit", limit)

        if offset is not None:
            params["offset"] = cls.validate_value("offset", offset)

        if robots is not None:
            params["robot"] = robots

        if from_date is not None:
            params["fromDate"] = validate_time(from_date)

        if to_date is not None:
            params["toDate"] = validate_time(to_date)

        if order_by is not None:
            params["order_by"] = order_by

        if order_dir is not None:
            params["order_dir"] = order_dir

        query_data = {
            "measurement": LOGS_MEASUREMENT,
            "query_data": params,
            "count_field": "alert_id",
        }

        query_response = await message_client.send_request(
            ALERT_QUERY_HANDLER_MSG_TYPE, query_data, None, True
        )

        return AlertQueryResponse(**(query_response["response"]))
