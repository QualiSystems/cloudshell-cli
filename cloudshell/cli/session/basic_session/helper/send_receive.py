import time
from typing import TYPE_CHECKING, Optional

from cloudshell.cli.session.basic_session.exceptions import SessionReadTimeout, SessionReadEmptyData, SessionException

if TYPE_CHECKING:
    from cloudshell.cli.session.basic_session.core.session import AbstractSession


def send_line(session: "AbstractSession", command: str, new_line: str = "\r") -> None:
    """Add new line to the end of command string and send."""
    session.send(command + new_line)


def receive_all(session: "AbstractSession", timeout: int = 30) -> str:
    """Read as much as possible before catch SessionTimeoutException."""
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


def clear_buffer(session: "AbstractSession", timeout: Optional[int] = None) -> str:
    """Clear buffer."""
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


def check_active(session: "AbstractSession", timeout: int = 1) -> bool:
    send_line(session, "")
    data = receive_all(session, timeout)
    return bool(data)
