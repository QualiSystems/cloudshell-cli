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
    def hardware_expect(self, command=None, expected_string=None, action_map=OrderedDict(), error_map=OrderedDict(),
                        timeout=None, retries=None, check_action_loop_detector=True, empty_loop_timeout=None,
                        logger=None, **optional_args):
        pass

    @abstractmethod
    def reconnect(self, prompt):
        pass

    @abstractmethod
    def _default_actions(self):
        pass
