from cloudshell.cli.service.cli_service import CliService
from cloudshell.cli.session.connection_manager import ConnectionManager
import inject


def bindings(binder):
    """
    Bindings for cli package
    :param binder: The Binder object for binding creation
    :type binder: inject.Binder

    """

    """Binding for session object"""
    _SESSION = 'session'
    try:
        binder.bind_to_provider(_SESSION, ConnectionManager.get_thread_session)
        # binder.bind_to_provider(_SESSION, ConnectionManager.get_session)
    except inject.InjectorException:
        pass

    """Binding for connection manager"""
    _CONNECTION_MANAGER = 'connection_manager'
    try:
        binder.bind_to_constructor(_CONNECTION_MANAGER, ConnectionManager)
    except inject.InjectorException:
        pass

    """Binding for CLI service"""
    _CLI_SERVICE = 'cli_service'
    try:
        binder.bind_to_provider(_CLI_SERVICE, CliService)
    except inject.InjectorException:
        pass
