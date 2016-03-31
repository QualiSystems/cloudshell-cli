class SessionTypes(object):
    _REGISTERED_TYPES = {}

    class SType:
        def __init__(self, name, classobj=None):
            self._name = name
            self._classobj = classobj

        @property
        def classobj(self):
            if not self._classobj:
                raise Exception('Session does not registered')
            return self._classobj

        @classobj.setter
        def classobj(self, classobj):
            self._classobj = classobj
            SessionTypes._REGISTERED_TYPES[self._name] = classobj

        @property
        def name(self):
            return self._name

        @name.setter
        def name(self, name):
            self.name = name

        def __eq__(self, other):
            if other and isinstance(other, SessionTypes.SType):
                return other.name == self.name and other.classobj == self.classobj
            elif other and isinstance(other, str):
                return other.lower() == self.name


    SSH = SType('ssh')
    CONSOLE = SType('console')
    TCP = SType('tcp')
    TELNET = SType('telnet')

    @staticmethod
    def get_registered_types():
        return SessionTypes._REGISTERED_TYPES.values()
