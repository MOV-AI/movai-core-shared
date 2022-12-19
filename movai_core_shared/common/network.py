import socket


def get_ip_address() -> str:
    """Returns the host(container) ip address.

    Returns:
        str: The ip address of the host.
    """
    hostname = socket.gethostname()
    ip_addr = socket.gethostbyname(hostname)
    return ip_addr