"""
   Copyright (C) Mov.ai  - All Rights Reserved
   Unauthorized copying of this file, via any medium is strictly prohibited
   Proprietary and confidential

   Developers:
   - Erez Zomer  (erez@mov.ai) - 2022
"""

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