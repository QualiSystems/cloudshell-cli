from abc import ABCMeta


class ConnectionParams(object):
    """
    Session parameters
    """
    __metaclass__ = ABCMeta

    def __init__(self, host, port=None, on_session_start=None):
        self.host = host
        self.port = None

        if port and int(port) != 0:
            self.port = int(port)

        if host:
            temp_host = host.split(':')
            self.host = temp_host[0]
            if not self.port and len(temp_host) > 1:
                self.port = int(temp_host[1])
        else:
            self.host = host

        self.on_session_start = on_session_start

    def __eq__(self, other):
        """
        :param other:
        :type other: ConnectionParams
        :return:
        :rtype: bool
        """
        return self.__class__ == other.__class__ and self.host == other.host and self.port == other.port
