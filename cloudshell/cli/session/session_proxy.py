import inject
from cloudshell.configuration.cloudshell_cli_bindings import CONNECTION_MANAGER


class ReturnToPoolProxy(object):
    """Proxy class, return session back to pool when GC destruct session"""

    def __init__(self, instance):
        self._instance = instance

    def __getattr__(self, name):
        return getattr(self._instance, name)

    def __del__(self):
        if inject and inject.is_configured():
            cm = inject.instance(CONNECTION_MANAGER)
            cm.return_session_to_pool(self)
