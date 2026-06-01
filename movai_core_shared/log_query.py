from movai_core_shared.consts import (
    DEFAULT_LOG_LIMIT,
    DEFAULT_LOG_OFFSET,
    LOGS_QUERY_HANDLER_MSG_TYPE,
    LOGS_MEASUREMENT,
)
from movai_core_shared.envvars import (
    LOCAL_MESSAGE_SERVER,
    MASTER_MESSAGE_SERVER,
)
from movai_core_shared.messages.metric_data import LogQueryResponse
from movai_core_shared.core.message_client import AsyncMessageClient
from movai_core_shared.common.utils import is_manager
from movai_core_shared.common.time import validate_time
from .base_query import BaseQuery


# pylint: disable=too-many-arguments,too-many-locals,too-many-branches,invalid-name


class LogsQuery(BaseQuery):
    """A class for querying logs"""

    @classmethod
    async def get_logs(
        cls,
        limit=DEFAULT_LOG_LIMIT,
        offset=DEFAULT_LOG_OFFSET,
        robots=None,
        services=None,
        level=None,
        message=None,
        fromDate=None,
        toDate=None,
        order_by=None,
        order_dir=None,
        **kwrargs,
    ) -> LogQueryResponse:
        """Get logs from message-server"""
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

        if level is not None:
            params["level"] = level

        if message is not None:
            params["message"] = cls.validate_message(message)

        if fromDate is not None:
            params["fromDate"] = validate_time(fromDate)

        if toDate is not None:
            params["toDate"] = validate_time(toDate)

        if services is not None:
            params["service"] = services

        if order_by is not None:
            params["order_by"] = order_by

        if order_dir is not None:
            params["order_dir"] = order_dir

        if kwrargs:
            if "tags" in kwrargs:
                params["tag"] = kwrargs["tags"]
            else:
                params["tag"] = kwrargs

        query_data = {
            "measurement": LOGS_MEASUREMENT,
            "query_data": params,
            "count_field": "message",
        }

        query_response = await message_client.send_request(
            LOGS_QUERY_HANDLER_MSG_TYPE, query_data, None, True
        )

        return LogQueryResponse(**(query_response["response"]))
