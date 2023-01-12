from datetime import datetime

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

def delta_time_int(delta: int) -> int:
    """returns a future time in timestamp format.

    Args:
        expiration_delta (int): the time delta from now.

    Returns:
        int: an int representing the time delta.
    """
    return int((datetime.now() + delta).timestamp())

def delta_time_float(delta: int) -> float:
    """returns a future time in timestamp format.

    Args:
        expiration_delta (int): the time delta from now.

    Returns:
        float: an float representing the time delta.
    """
    return (datetime.now() + delta).timestamp()
