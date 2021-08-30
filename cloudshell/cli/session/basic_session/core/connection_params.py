from abc import ABCMeta

ABC = ABCMeta("ABC", (object,), {"__slots__": ()})


class ConnectionParams(ABC):
    """Session parameters."""

    def __init__(self, hostname, port=None, on_session_start=None):
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

        self.on_session_start = on_session_start

    def _on_session_start(self, logger):
        if self.on_session_start and callable(self.on_session_start):
            self.on_session_start(self, logger)

    def __eq__(self, other):
        """Is equal.

        :type other: ConnectionParams
        :rtype: bool
        """
        return (
                self.__class__ == other.__class__
                and self.hostname == other.hostname
                and self.port == other.port
        )
