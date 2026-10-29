"""Copyright (C) Mov.ai  - All Rights Reserved
Unauthorized copying of this file, via any medium is strictly prohibited
Proprietary and confidential

Developers:
- Erez Zomer (erez@mov.ai) - 2023
"""
from typing import Optional
import json

from pydantic import BaseModel, ConfigDict


class LogTags(BaseModel):
    # actual tags are part of this structure so we must allow extra
    model_config = ConfigDict(extra="allow")

    robot: str
    level: str
    service: str
    runtime: bool = False


class LogFields(BaseModel):
    module: str
    funcName: str
    lineno: int
    message: str
    args: Optional[str] = None  # json string

    def format(self) -> str:
        """Format log message.

        Returns:
            str: The formatted log message.

        """
        if self.args:
            try:
                self.message = self.message % (tuple(json.loads(self.args)))
                self.args = None  # clear args after formatting
            except TypeError:
                self.message = (
                    f"Failed to format log message '{self.message}' with args {self.args}"
                )
                self.args = None  # clear args after formatting
