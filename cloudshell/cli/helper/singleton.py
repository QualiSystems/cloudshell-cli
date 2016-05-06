__author__ = 'g8y3e'
"""
Classical pattern singleton.
Example wiki: https://en.wikipedia.org/wiki/Singleton_pattern
"""
import threading


# class Singleton(type):
#     _instances = {}
#
#     def __call__(cls, *args, **kwargs):
#         if cls not in cls._instances:
#             cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
#
#         return cls._instances[cls]


class Singleton(object):
    _instance = None
    _SINGLETON_LOCK = threading.Lock()

    def __new__(cls, *args, **kwargs):

        if not isinstance(cls._instance, cls):
            with cls._SINGLETON_LOCK:
                cls._instance = object.__new__(cls, *args, **kwargs)
        return cls._instance

    @classmethod
    def is_defined(cls):
        defined = False
        if cls._instance:
            defined = True
        return defined
