"""
   Copyright (C) Mov.ai  - All Rights Reserved
   Unauthorized copying of this file, via any medium is strictly prohibited
   Proprietary and confidential

   Developers:
   - Moawiya Mograbi (moawiya@mov.ai) - 2023
"""
from typing import List

import pydantic


class SMSData(pydantic.BaseModel):
    recipients: List[str]
    msg: str
    notification_type: str
