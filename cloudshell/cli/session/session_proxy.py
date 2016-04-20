import inject


class ReturnToPoolProxy(object):
    """Proxy class, return session back to pool when GC destruct session"""

    def __init__(self, instance):
        self._instance = instance

    def __getattr__(self, name):
        return getattr(self._instance, name)

    def __del__(self):
        if inject and inject.is_configured():
            cm = inject.instance('connection_manager')
            cm.return_session_to_pool(self)
