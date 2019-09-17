from abc import ABCMeta

ABC = ABCMeta("ABC", (object,), {"__slots__": ()})


class ConnectionParams(ABC):
    """Session parameters."""

    def __init__(self, host, port=None, on_session_start=None, pkey=None):
        self.host = host
        self.port = None

        if port and int(port) != 0:
            self.port = int(port)

        if host:
            temp_host = host.split(":")
            self.host = temp_host[0]
            if not self.port and len(temp_host) > 1:
                self.port = int(temp_host[1])
        else:
            self.host = host

        self.on_session_start = on_session_start
        self.pkey = pkey

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
            and self.host == other.host
            and self.port == other.port
            and self.pkey == other.pkey
        )
