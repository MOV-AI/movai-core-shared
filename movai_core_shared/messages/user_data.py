"""
   Copyright (C) Mov.ai  - All Rights Reserved
   Unauthorized copying of this file, via any medium is strictly prohibited
   Proprietary and confidential

   Developers:
   - Moawiya Mograbi (moawiya@mov.ai) - 2023
"""
import pydantic


class UserData(pydantic.BaseModel):
    notification_type: str = "user"
    msg: str
    robot_id: str
    robot_name: str
