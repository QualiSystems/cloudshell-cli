import inject
from cloudshell.configuration.cloudshell_cli_binding_keys import CONNECTION_MANAGER


class ReturnToPoolProxy(object):
    """Proxy class, return session back to pool when GC destruct session"""

    VALIDATED_CALLS = ('connect', 'reconnect')

    def __init__(self, instance):
        self._instance = instance
        self._valid = False

    def __getattr__(self, name):
        attr = getattr(self._instance, name)
        if callable(attr):
            attr = self.call_wrapper(name, attr)
        return attr

    def call_wrapper(self, name, attr):
        def wrapper_func(*args, **kwargs):
            try:
                result = attr(*args, **kwargs)
                if name in self.VALIDATED_CALLS:
                    self._valid = True
                return result
            except:
                self._valid = False
                raise
        return wrapper_func

    def __del__(self):
        if inject and inject.is_configured() and self._valid:
            cm = inject.instance(CONNECTION_MANAGER)
            cm.return_session_to_pool(self)
