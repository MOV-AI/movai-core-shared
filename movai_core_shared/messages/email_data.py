"""
   Copyright (C) Mov.ai  - All Rights Reserved
   Unauthorized copying of this file, via any medium is strictly prohibited
   Proprietary and confidential

   Developers:
   - Moawiya Mograbi (moawiya@mov.ai) - 2023
"""
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, field_validator

from movai_core_shared.envvars import FLEET_NAME, DEVICE_NAME
from movai_core_shared.consts import NOTIFICATIONS_HANDLER_MSG_TYPE
from movai_core_shared.logger import Log


logger = Log.get_logger(NOTIFICATIONS_HANDLER_MSG_TYPE)


class EmailData(BaseModel):
    """
    a base dataclass based on pydantic basemodel in order to support
    validation and check for missing fields or wrong values.
    """

    recipients: List[EmailStr]
    notification_type: str = "smtp"
    subject: Optional[str] = None
    body: str
    attachment_data: Optional[str] = None
    sender: str = f"{DEVICE_NAME} {FLEET_NAME}"

    @field_validator("notification_type")
    @classmethod
    def notification_type_valid(cls, value):
        """Validates the notification_type field

        Args:
            value (str): Which notification to use.

        Raises:
            ValueError: In case notification is diffenrent from smtp.

        Returns:
            str: The given value.
        """
        if value.lower() != "smtp":
            raise ValueError("notification_type must be smtp")
        return value

    model_config = ConfigDict(frozen=False)
