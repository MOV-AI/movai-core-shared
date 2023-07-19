"""
   Copyright (C) Mov.ai  - All Rights Reserved
   Unauthorized copying of this file, via any medium is strictly prohibited
   Proprietary and confidential

   Developers:
   - Erez Zomer (erez@mov.ai) - 2023
"""
from pydantic import BaseModel

from movai_core_shared.messages.general_data import Request


class StressData(BaseModel):
    current: int
    total: int

class StressRequest(Request):
    req_data: StressData