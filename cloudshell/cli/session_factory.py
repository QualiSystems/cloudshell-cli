from abc import ABCMeta, abstractmethod


class SessionFactory(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def new_session(self, session_type, connection_attrs, prompt, logger):
        """
        Create new session specified type
        :param session_type:
        :param prompt:
        :param logger:
        :param session_attributes:
        :return:
        """
        pass
