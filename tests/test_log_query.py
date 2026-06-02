"""Tests for log_query module"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from movai_core_shared.log_query import LogsQuery
from movai_core_shared.messages.metric_data import LogQueryResponse


@pytest.mark.asyncio
@patch("movai_core_shared.log_query.is_manager")
@patch("movai_core_shared.log_query.AsyncMessageClient")
async def test_get_logs_basic(mock_message_client_class, mock_is_manager):
    """Test basic get_logs functionality"""
    # Setup mocks
    mock_is_manager.return_value = False
    mock_client_instance = MagicMock()
    mock_message_client_class.return_value = mock_client_instance

    # Mock the send_request response with correct structure
    mock_response = {
        "response": {
            "success": True,
            "results": {
                "limit": 100,
                "offset": 0,
                "count": 1,
                "data": [
                    {
                        "time": 1234567890,
                        "robot": "robot1",
                        "level": "INFO",
                        "service": "test_service",
                        "module": "test_module",
                        "funcName": "test_func",
                        "lineno": 42,
                        "message": "test log",
                    }
                ],
            },
        }
    }
    mock_client_instance.send_request = AsyncMock(return_value=mock_response)

    # Call the method
    result = await LogsQuery.get_logs(limit=100, offset=0, level="INFO", robots=["robot1"])

    # Assertions
    assert isinstance(result, LogQueryResponse)
    assert result.success is True
    assert result.results.limit == 100
    assert result.results.offset == 0
    assert result.results.count == 1
    assert len(result.results.data) == 1
    assert result.results.data[0].message == "test log"
    assert result.results.data[0].level == "INFO"
    mock_client_instance.send_request.assert_called_once()


@pytest.mark.asyncio
@patch("movai_core_shared.log_query.is_manager")
@patch("movai_core_shared.log_query.AsyncMessageClient")
async def test_get_logs_default_params(mock_message_client_class, mock_is_manager):
    """
    Test get_logs with minimal parameters

    This test ensures that get_logs can be called with no parameters
    and still returns a valid response, using default values
    """
    # Setup mocks
    mock_is_manager.return_value = True  # Test manager branch
    mock_client_instance = MagicMock()
    mock_message_client_class.return_value = mock_client_instance

    mock_response = {
        "response": {
            "success": True,
            "results": {"limit": 1000, "offset": 0, "count": 0, "data": []},
        }
    }
    mock_client_instance.send_request = AsyncMock(return_value=mock_response)

    # Call with no parameters
    result = await LogsQuery.get_logs()

    # Assertions
    assert isinstance(result, LogQueryResponse)
    assert result.success is True
    assert result.results.count == 0
    assert len(result.results.data) == 0
    mock_client_instance.send_request.assert_called_once()
