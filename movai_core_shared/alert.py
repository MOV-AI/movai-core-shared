"""Alert query."""
from movai_core_shared.consts import (
    ALERT_QUERY_HANDLER_MSG_TYPE,
    DEFAULT_LOG_LIMIT,
    DEFAULT_LOG_OFFSET,
    LOGS_MEASUREMENT,
    MIN_LOG_QUERY,
    MAX_LOG_QUERY,
)
from movai_core_shared.envvars import (
    LOCAL_MESSAGE_SERVER,
    MASTER_MESSAGE_SERVER,
)
from movai_core_shared.messages.metric_data import AlertQueryResponse
from movai_core_shared.core.message_client import AsyncMessageClient
from movai_core_shared.common.utils import is_manager
from movai_core_shared.common.time import validate_time

# pylint: disable=too-many-arguments


class AlertQuery:
    """A class for querying alert."""

    _min_val = MIN_LOG_QUERY
    _max_val = MAX_LOG_QUERY

    @classmethod
    async def get_logs(
        cls,
        limit=DEFAULT_LOG_LIMIT,
        offset=DEFAULT_LOG_OFFSET,
        robots=None,
        from_date=None,
        to_date=None,
        order_by=None,
        order_dir=None,
    ) -> AlertQueryResponse:
        """Get logs from message-server"""
        server_addr = MASTER_MESSAGE_SERVER
        if is_manager():
            server_addr = LOCAL_MESSAGE_SERVER

        message_client = AsyncMessageClient(server_addr)
        params = {}

        if limit is not None:
            params["limit"] = limit

        if offset is not None:
            params["offset"] = offset

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
