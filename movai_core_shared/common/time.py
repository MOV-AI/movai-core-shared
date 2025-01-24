from datetime import datetime, timedelta
from typing import Union

from movai_core_shared.exceptions import TimeError


def current_time_string() -> str:
    """Returns the current time as a string in the format:
    d/m/Y at H:M:S
    Returns:
        str: a string reporesenting current time.
    """
    return datetime.now().strftime("%d/%m/%Y at %H:%M:%S")


def current_timestamp_float() -> float:
    """Returns the current time as a float.

    Returns:
        float: a float represnt current time.
    """
    return datetime.now().timestamp()


def current_timestamp_int() -> int:
    """Returns current time as an int.

    Returns:
        int: An int representing current time.
    """
    return int(datetime.now().timestamp())


def delta_time_int(delta: timedelta) -> int:
    """returns a future time in timestamp format.

    Args:
        expiration_delta (timedelta): the time delta from now.

    Returns:
        int: an int representing the time delta.
    """
    return int((datetime.now() + delta).timestamp())


def delta_time_float(delta: timedelta) -> float:
    """returns a future time in timestamp format.

    Args:
        expiration_delta (timedelta): the time delta from now.

    Returns:
        float: an float representing the time delta.
    """
    return (datetime.now() + delta).timestamp()


def validate_timestamp(timestamp: int) -> int:
    """Validates a timestamp is in correct format.

    Args:
        timestamp (int): The timestamp to validate

    Raises:
        TimeError: In case the timestamp is in the wrong format.

    Returns:
        int: The validated timestamp.
    """
    try:
        timestamp = datetime.fromtimestamp(timestamp)
        return timestamp
    except (ValueError, TypeError) as exc:
        raise TimeError("The supplied time argument is not in timestamp format!") from exc


def validate_time(value: Union[int, str]) -> int:
    """Validate if value is timestamp or datetime

    Args:
        value (int|str): The datetime to validate

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
        except Exception as exc:
            raise ValueError(
                "invalid datetime value, expected: <timestamp> | %Y-%m-%d %H:%M:%S"
            ) from exc

    return int(dt_obj.timestamp())
