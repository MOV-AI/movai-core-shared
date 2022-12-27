"""
   Copyright (C) Mov.ai  - All Rights Reserved
   Unauthorized copying of this file, via any medium is strictly prohibited
   Proprietary and confidential

   Usage:
        Holds various general functions related to robot configuration.

   Developers:
   - Erez Zomer (erez@mov.ai) - 2022
"""
from movai_core_shared.envvars import REDIS_MASTER_HOST

def is_manager() -> bool:
    """Tell the process if its running on the manager host machine.

    Returns:
        bool: true if the fuction runs on a manager host machine, false otherwise.
    """
    return REDIS_MASTER_HOST == "redis-master"


def is_enteprise() -> bool:
    """This function check the existence of the movai_core_enterprise package.

    Returns:
        bool: True if import succeeds, False otherwise.
    """
    try:
        import movai_core_enterprise
        return True
    except ImportError:
        return False
