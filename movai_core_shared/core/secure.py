"""
   Copyright (C) Mov.ai  - All Rights Reserved
   Unauthorized copying of this file, via any medium is strictly prohibited
   Proprietary and confidential

   Developers:
   - Erez Zomer  (erez@mov.ai) - 2022
"""
import secrets
import os
import zmq.asyncio

from stat import S_IRGRP, S_IROTH, S_IRUSR

def generate_secret_bytes(length: int=32) -> bytes:
    """The function generates a unique secret in bytes format,

    Args:
        length (int, optional): the length of the secret. Defaults to 32.

    Returns:
        bytes: the generated secret.
    """
    return secrets.token_bytes(length)


def generate_secret_string(length: int=32) -> bytes:
    """The function generates a unique secret in bytes format,

    Args:
        length (int, optional): the length of the secret. Defaults to 32.

    Returns:
        bytes: the generated secret.
    """
    return secrets.token_urlsafe(length)


def generate_key_pair() -> tuple:
    public_key, secret_key = zmq.curve_keypair()
    return public_key, secret_key


def get_client_keys(dir_name: str, key_name: str) -> tuple:
    base_filename = os.path.join(dir_name, key_name)
    if os.path.exists(f"{base_filename}.public") and os.path.exists(
        f"{base_filename}.secret"
    ):
        with open(base_filename + ".public", "r", encoding="utf8") as f:
            public_key = f.readlines()[0].encode("utf8")
        with open(base_filename + ".secret", "r", encoding="utf8") as f:
            secret_key = f.readlines()[0].encode("utf8")
        return public_key, secret_key
    else:
        return (None, None)


def create_client_keys(dir_name: str, key_name: str) -> tuple:
    public_key, secret_key = get_client_keys(dir_name, key_name)
    if public_key is not None and secret_key is not None:
        return public_key, secret_key
    public_key, secret_key = generate_key_pair()
    base_filename = os.path.join(dir_name, key_name)
    with open(base_filename + ".public", "w", encoding="utf8") as f:
        f.write(public_key.decode("utf8"))
        os.chmod(base_filename + ".public", S_IRUSR | S_IRGRP | S_IROTH)
    with open(base_filename + ".secret", "w", encoding="utf8") as f:
        f.write(secret_key.decode("utf8"))
        os.chmod(base_filename + ".secret", S_IRUSR)
    return public_key, secret_key
