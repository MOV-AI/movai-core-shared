"""
Recovery file holds const and enum used by the recovery module.

Copyright (C) Mov.ai  - All Rights Reserved
Unauthorized copying of this file, via any medium is strictly prohibited
Proprietary and confidential

Developers:
- Dor Marcous (Dor@mov.ai) - 2023
"""
from enum import Enum, auto

RECOVERY_TIMEOUT_IN_SECS = 15
RECOVERY_STATE_KEY = "recovery_state"
RECOVERY_RESPONSE_KEY = "recovery_response"


class RecoveryStates(Enum):
    """Class for keeping recovery states.
    Values are stored in recovery_state fleet variable."""

    READY = auto()
    IN_RECOVERY = auto()
    PUSHED = auto()
    NOT_AVAILABLE = auto()
