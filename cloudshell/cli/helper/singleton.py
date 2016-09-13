__author__ = 'g8y3e'
"""
Classical pattern singleton.
Example wiki: https://en.wikipedia.org/wiki/Singleton_pattern
"""
import threading


class Singleton(object):
    _instance = None
    _SINGLETON_LOCK = threading.Lock()

    def __new__(cls, *args, **kwargs):
        with cls._SINGLETON_LOCK:
            if not cls._instance:
                cls._instance = object.__new__(cls, *args, **kwargs)
            return cls._instance

#
#     @classmethod
#     def is_defined(cls):
#         defined = False
#         if cls._instance:
#             defined = True
#         return defined
