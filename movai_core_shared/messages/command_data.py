from pydantic import BaseModel
from movai_core_shared.messages.general_data import Request

class Source(BaseModel):
    IP: str
    host: str
    id: str

class Destination(Source):
    pass

class Command(BaseModel):
    command: str
    flow: str
    dst: Destination

    def __str__(self):
        return f"Command: {self.command}\n Flow: {self.flow}\n"


class CommandReq(Request):
    req_data: Command
