from cloudshell.cli.connection_manager import ConnectionManager

def bindings(binder):
    """Binding for context"""
    binder.bind_to_constructor('connection_manager', ConnectionManager)
