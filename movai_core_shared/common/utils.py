"""
   Copyright (C) Mov.ai  - All Rights Reserved
   Unauthorized copying of this file, via any medium is strictly prohibited
   Proprietary and confidential

   Usage:
        Holds various general functions related to robot configuration.

   Developers:
   - Erez Zomer (erez@mov.ai) - 2022
"""
import asyncio
import socket
from movai_core_shared.envvars import REDIS_MASTER_HOST


def is_manager() -> bool:
    """Identify if this robot is the manager host machine.

    Returns:
        bool: true if the fuction runs on a manager host machine, false otherwise.
    """
    return REDIS_MASTER_HOST in (None, "redis-master")


def is_enterprise() -> bool:
    """Check the existence of the movai_core_enterprise package.

    Returns:
        bool: True if import succeeds, False otherwise.
    """
    try:
        import movai_core_enterprise

        return True
    except ImportError:
        return False


def create_principal_name(domain_name: str, account_name: str) -> str:
    """build principal name -> "account_name@domain_name

    Args:
    domain_name (str): the name of the domain which the user belongs to.
    account_name (str): the account name of the user.

    Returns:
        (str): the name in the form account_name@domain_name
    """
    principal_name = f"{account_name}@{domain_name}"
    return principal_name


def get_ip_address() -> str:
    """Returns the host(container) ip address.

    Returns:
        str: The ip address of the host.
    """
    hostname = socket.gethostname()
    ip_addr = socket.gethostbyname(hostname)
    return ip_addr


async def run_blocking_code(executor, blocking_func, *args):
    """runs a blocking code in another thread to free the main loop for other tasks.

    Args:
        executor (_type_): A thread or process to execute the code.
        blocking_func (_type_): The fucntion to execute.

    Returns:
        Any: The results from the blocking_func
    """
    loop = asyncio.get_running_loop()
    future = loop.run_in_executor(executor, blocking_func, *args)
    results = await future
    return results
