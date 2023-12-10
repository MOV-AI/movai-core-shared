"""
   Copyright (C) Mov.ai  - All Rights Reserved
   Unauthorized copying of this file, via any medium is strictly prohibited
   Proprietary and confidential

   Developers:
   - Moawiya Mograbi (moawiya@mov.ai) - 2023
"""
from re import search
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, field_validator

from movai_core_shared.envvars import FLEET_NAME, DEVICE_NAME
from movai_core_shared.consts import NOTIFICATIONS_HANDLER_MSG_TYPE
from movai_core_shared.logger import Log


EMAIL_REGEX = r"([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+"
logger = Log.get_logger(NOTIFICATIONS_HANDLER_MSG_TYPE)


class EmailData(BaseModel):
    """
    a base dataclass based on pydantic basemodel in order to support
    validation and check for missing fields or wrong values.
    """

    recipients: List[str]
    notification_type: str = "smtp"
    subject: Optional[str] = None
    body: str
    attachment_data: Optional[str] = None
    sender: str = f"{DEVICE_NAME} {FLEET_NAME}"

    @field_validator("notification_type")
    @classmethod
    def notification_type_valid(cls, value):
        if value.lower() != "smtp":
            raise ValueError("notification_type must be smtp")
        return value

    @field_validator("recipients")
    @classmethod
    def recipients_valid(cls, value):
        valid = []
        for email in value:
            if not search(EMAIL_REGEX, email):
                logger.warning(f"email {email} is not a valid email address")
            else:
                valid.append(email)
        if not valid:
            raise ValueError("no valid Email Address provided for email notification")

        return valid

    model_config = ConfigDict(frozen=False)
