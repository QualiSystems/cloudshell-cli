import types


class SessionCreator(object):
    """Creator for session"""

    def __init__(self, classobj):
        """Classobj for session"""
        self.classobj = classobj
        """Classobj for proxy"""
        self.proxy = None
        """Dict that contains keys and funcs or values, used like a key dictionary when creates session object"""
        self.kwargs = None

    def create_session(self):
        """Creates session object
        :rtype: Session
        :raises: Exception
        """

        kwargs = {}
        for key in self.kwargs:
            if callable(self.kwargs[key]):
                kwargs[key] = self.kwargs[key]()
            else:
                kwargs[key] = self.kwargs[key]

        if self.classobj and isinstance(self.classobj, types.ObjectType):
            if self.proxy and isinstance(self.proxy, types.ObjectType):
                return self.proxy(self.classobj(**kwargs))
            else:
                return self.classobj(**kwargs)
        else:
            raise Exception('SessionCreator', 'Incorrect classobj for session \'{0}\''.format(self.classobj))
