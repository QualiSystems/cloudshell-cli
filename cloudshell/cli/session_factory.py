from abc import ABCMeta, abstractmethod


class SessionFactoryException(Exception):
    pass


class SessionFactory(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def new_session(self, session_type, prompt, logger, **session_attributes):
        """
        Create new session specified type
        :param session_type:
        :param prompt:
        :param logger:
        :param session_attributes:
        :return:
        """
        pass
