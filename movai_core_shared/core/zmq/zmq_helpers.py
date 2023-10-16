import json
from logging import getLogger
import random

from movai_core_shared.envvars import DEVICE_NAME, SERVICE_NAME
from movai_core_shared.exceptions import MessageError

LOGGER = getLogger(__name__)


def create_msg(msg: dict):
    """create the msg in json format.

    Args:
        msg (dict): A dictionary format of the messge.

    Returns:
        json string
    """
    if not isinstance(msg, dict):
        return None
    try:
        data = json.dumps(msg).encode("utf8")
        return data
    except (json.JSONDecodeError, TypeError) as error:
        LOGGER.error(
            f"Got error of type {error.__class__.__name__} while trying to convert dictionary to json."
        )
        return None

def extract_reponse(buffer: bytes):
    """Extracts the response from the buffer.

    Args:
        buffer (bytes): The memory buffer which contains the response msg.

    Returns:
        (dict): A response from server.
    """
    index = len(buffer) - 1
    msg = buffer[index]

    if msg is None:
        raise MessageError("Got an empty msg!")

    try:
        response = json.loads(msg)
        return response
    except (json.JSONDecodeError, TypeError) as error:
        LOGGER.error(
            f"Got error of type {error.__class__.__name__} while trying to recieve the message."
        )
        return {}

def generate_zmq_identity(zmq_type: str) -> str:
    random.seed()  # setting the seed for the random number generator
    identity = f"{DEVICE_NAME}_{SERVICE_NAME}_{zmq_type}_{random.getrandbits(24)}"
    return identity