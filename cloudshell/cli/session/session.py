__author__ = 'g8y3e'

from abc import ABCMeta, abstractmethod
from collections import OrderedDict


class Session:
    __metaclass__ = ABCMeta

    @abstractmethod
    def connect(self, re_string=''):
        pass

    @abstractmethod
    def disconnect(self):
        pass

    @abstractmethod
    def _send(self, data_str):
        pass

    @abstractmethod
    def _receive(self, timeout=None):
        pass

    @abstractmethod
    def hardware_expect(self, data_str=None, re_string='', expect_map=OrderedDict(),
                        error_map=OrderedDict(), timeout=None, retries_count=3):
        pass

    @abstractmethod
    def reconnect(self, prompt):
        pass

    @abstractmethod
    def _default_actions(self):
        pass
