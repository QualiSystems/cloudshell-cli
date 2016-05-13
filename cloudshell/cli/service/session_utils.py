from weakref import WeakKeyDictionary
from threading import currentThread

from cloudshell.cli.session.connection_manager import ConnectionManager

_SESSION_CONTAINER = WeakKeyDictionary()


def get_thread_session():
    if not currentThread() in _SESSION_CONTAINER:
        _SESSION_CONTAINER[currentThread()] = ConnectionManager.get_session()
    return _SESSION_CONTAINER[currentThread()]
