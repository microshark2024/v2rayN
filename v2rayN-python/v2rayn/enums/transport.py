"""Transport protocol enum."""

from enum import IntEnum


class ETransport(IntEnum):
    """Network transport protocols."""

    tcp = 0
    kcp = 1
    ws = 2
    httpupgrade = 3
    xhttp = 4
    h2 = 5
    http = 6
    quic = 7
    grpc = 8
