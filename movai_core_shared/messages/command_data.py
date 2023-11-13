from typing import Optional
from pydantic import BaseModel
from movai_core_shared.messages.general_data import Request

class Source(BaseModel):
    ip: str
    host: str
    id: str

class Destination(Source):
    pass

class CommandData(BaseModel):
    command: str
    flow: str
    node: Optional[str] = ""
    port: Optional[str] = ""
    data: Optional[dict] = ""

    def __str__(self):
        text = f"Command: {self.command}\n Flow: {self.flow}\n"
        if self.node:
            text += f"Node: {self.node}\n"
        
        if self.port:
            text += f"Port: {self.port}\n"
        
        if self.data:
            text == f"Data: {self.data}\n"

        return text

class Command(BaseModel):
    command: CommandData
    dst: Destination

    
class CommandReq(Request):
    req_data: Command
