from abc import ABCMeta
from typing import Optional, Union

ABC = ABCMeta("ABC", (object,), {"__slots__": ()})


class ConnectionParams(ABC):
    """Session parameters."""

    def __init__(self, hostname: str,
                 port: Optional[Union[str, int]] = None,
                 username: Optional[str] = None,
                 password: Optional[str] = None,
                 ):
        self.hostname = hostname
        self.port = None

        if port and int(port) != 0:
            self.port = int(port)

        if hostname:
            temp_host = hostname.split(":")
            self.hostname = temp_host[0]
            if not self.port and len(temp_host) > 1:
                self.port = int(temp_host[1])
        else:
            self.hostname = hostname

        self.username = username
        self.password = password

    def __eq__(self, other: "ConnectionParams"):
        """Is equal.

        :type other: ConnectionParams
        :rtype: bool
        """
        return (
                self.__class__ == other.__class__
                and self.hostname == other.hostname
                and self.port == other.port
                and self.username == other.username
                and self.password == other.password
        )
