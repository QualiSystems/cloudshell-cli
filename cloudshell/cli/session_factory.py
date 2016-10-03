from abc import ABCMeta, abstractmethod


class SessionFactoryException(Exception):
    pass


class SessionFactory(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def new_session(self, session_type, **session_attributes):
        pass
