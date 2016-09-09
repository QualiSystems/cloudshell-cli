from cloudshell.cli.service.cli_exceptions import CommandExecutionException


class SessionValidationProxy(object):
    """Proxy class for session validation"""

    """Call of those methods change state to valid"""
    VALIDATED_CALLS = ('connect', 'reconnect')

    """Those exceptions do not change state"""
    IGNORED_EXCEPTIONS = [CommandExecutionException]

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
            """
            Wrap session calls and change session state if exception was raised
            :param args:
            :param kwargs:
            :return:
            """
            try:
                result = attr(*args, **kwargs)
                if name in self.VALIDATED_CALLS:
                    self._valid = True
                return result
            except Exception as e:
                if e.__class__ not in self.IGNORED_EXCEPTIONS:
                    self._valid = False
                raise

        return wrapper_func

    def set_invalid(self):
        """Set session to invalid to remove it from session pull

        :return:
        """

        self._valid = False

    def is_valid(self):
        """
        Valid state
        :rtype: bool
        """
        return self._valid
