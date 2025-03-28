"""Command data message definition."""

from typing import Optional

from pydantic import BaseModel
import pydantic

from movai_core_shared.messages.general_data import Request


class Destination(BaseModel):
    ip: str
    host: str
    id: str


class CommandData(BaseModel):
    command: str
    flow: Optional[str] = ""
    node: Optional[str] = ""
    port: Optional[str] = ""
    data: Optional[dict] = {}

    # validate using Pydantic's methods to ensure either "flow" or "node" is provided
    @pydantic.model_validator(mode="after")
    def validate_flow_or_node(self):
        if self.command in ("START", "STOP") and not self.flow:
            raise ValueError("Flow must be provided for START and STOP commands")
        elif self.command in ("RUN", "KILL", "TRANS") and not self.node:
            raise ValueError("Node must be provided for RUN, KILL, and TRANS commands")

    def __str__(self):
        text = f"Command: {self.command}\n Flow: {self.flow}\n"
        if self.node:
            text += f"Node: {self.node}\n"

        if self.port:
            text += f"Port: {self.port}\n"

        if self.data:
            text += f"Data: {self.data}\n"

        return text


class Command(BaseModel):
    command_data: CommandData
    dst: Optional[Destination]


class CommandReq(Request):
    req_data: Command
