import logging
import time
from typing import TYPE_CHECKING, Optional

from cloudshell.cli.session.core.exception import SessionException

if TYPE_CHECKING:
    from cloudshell.cli.session.core.session import Session

logger = logging.getLogger(__name__)


def reconnect(session: "Session", timeout: Optional[int] = None):
    """Recconnect implementation."""
    logger.debug("Reconnect")
    timeout = timeout or session.config.reconnect_timeout

    call_time = time.time()
    while time.time() - call_time < timeout:
        try:
            session.disconnect()
            return session.connect()
        except Exception:
            logger.exception("Reconnect failed.")
    raise SessionException(
        "Reconnect unsuccessful, timeout exceeded, see logs for more details",
    )
