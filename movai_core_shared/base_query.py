"""Base query."""
from datetime import datetime

from movai_core_shared.consts import (
    MIN_LOG_QUERY,
    MAX_LOG_QUERY,
)


class BaseQuery:
    """A class for querying metrics."""

    _min_val: int = MIN_LOG_QUERY
    _max_val: int = MAX_LOG_QUERY

    @classmethod
    def validate_value(cls, filter_name: str, value: int) -> int:
        """Validates the limmit.

        Args:
            filter_name (str): Which filter called the validation function.
            value (int): The limit to validate.
            alternate_value (int): an alternative value in case of error.

        Raises:
            ValueError: in case limit can not be casted to int.

        Returns:
            int: The validated limit.
        """
        try:
            val = int(value)
        except ValueError:
            raise ValueError(f"{value} is Invalid {filter_name} value")

        if val < cls._min_val:
            raise ValueError(f"{filter_name} value: {value} must be greater than {cls._min_val}")
        if val > cls._max_val:
            raise ValueError(f"{filter_name} value: {value} must be lower than {cls._max_val}")

        return val

    @classmethod
    def validate_message(cls, value: str) -> str:
        """Validates the message

        Args:
            value (str): A message to validate

        Raises:
            ValueError: In case message is not a string.

        Returns:
            str: The message.
        """
        if not isinstance(value, str):
            raise ValueError("Invalid message, message must be a string.")
        return value

    @classmethod
    def validate_datetime(cls, value: int) -> int:
        """Validate if value is timestamp or datetime

        Args:
            value (int): The datetime to validate

        Raises:
            ValueError: In case value isn't a time format.

        Returns:
            int: a timestamp value.
        """
        try:
            dt_obj = datetime.fromtimestamp(int(value))
        except (ValueError, TypeError):
            try:
                dt_obj = datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
            except Exception:
                raise ValueError(
                    "invalid datetime value, expected: <timestamp> | %Y-%m-%d %H:%M:%S"
                )

        return int(dt_obj.timestamp())
