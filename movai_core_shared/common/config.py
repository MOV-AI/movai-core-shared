from movai_core_shared.envvars import REDIS_MASTER_HOST

def is_manager() -> bool:
    """Tell the process if its running on the manager host machine.

    Returns:
        bool: true if the fuction runs on a manager host machine, false otherwise.
    """
    return REDIS_MASTER_HOST == "redis-master"