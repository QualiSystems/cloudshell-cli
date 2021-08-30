import time

# from cloudshell.cli.session.basic_session.core.session import BasicSession
from cloudshell.cli.session.basic_session.exceptions import SessionReadTimeout, SessionReadEmptyData, SessionException


def send_line(session, command, new_line="\r"):
    """Add new line to the end of command string and send.

    :param cloudshell.cli.session.basic_session.model.session.AbstractSession session:
    :param str command:
    :param str new_line:
    """
    session.send(command + new_line)


def receive_all(session, timeout=30):
    """Read as much as possible before catch SessionTimeoutException.

    :param cloudshell.cli.session.basic_session.model.session.AbstractSession session:
    :param int timeout:
    :rtype: str
    """
    start_time = time.time()
    read_buffer = ""
    while True:
        try:
            read_buffer += session.receive(0.1)
        except (SessionReadTimeout, SessionReadEmptyData):
            if read_buffer:
                return read_buffer
            elif time.time() - start_time > timeout:
                raise SessionException("Socket closed by timeout")


def clear_buffer(session, timeout=None):
    """Clear buffer.
    """
    out = ""
    if not timeout:
        timeout = session.config.clear_buffer_timeout
    while True:
        try:
            read_buffer = session.receive(timeout)
        except (SessionReadTimeout, SessionReadEmptyData):
            read_buffer = None
        if read_buffer:
            out += read_buffer
        else:
            break
    return out
