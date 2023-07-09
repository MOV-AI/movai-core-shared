from pydantic import BaseModel


def print_dict(message: dict, space_count: int):
    spacing = " " * 4
    text = ""
    for key, val in message.items():
        if hasattr(val, "__dict__"):
            text += print_dict(val.__dict__, space_count + 1)
        else:
            text += space_count * spacing + f"{key}: {val}\n"
    return text


class RobotInfo(BaseModel):
    """
    a base dataclass based on pydantic basemodel in order to support
    validation and check for missing fields or wrong values.
    """

    fleet: str
    robot: str
    service: str
    id: str


class Request(BaseModel):
    req_type: str
    created: int
    response_required: bool
    robot_info: RobotInfo

    def __str__(self):
        text = "\n" + "=" * 100 + "\n"
        text += print_dict(self.__dict__, 0)
        text += "=" * 100 + "\n"
        return text
