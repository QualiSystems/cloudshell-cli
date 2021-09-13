import logging
import time
from typing import TYPE_CHECKING

from cloudshell.cli.process.command.exception import SessionLoopLimitException
from cloudshell.cli.process.command.helper.reader_helper import normalize_buffer
from cloudshell.cli.session.helper.send_receive import receive_all

if TYPE_CHECKING:
    from cloudshell.cli.session.core.session import Session

logger = logging.getLogger(__name__)


class ResponseBuffer(object):
    def __init__(self):
        self._read_iterations = [""]
        self.command_removed = False

    def _validate(self, data: str) -> str:
        return normalize_buffer(data)

    def append_last(self, data: str) -> None:
        self._read_iterations[-1] += self._validate(data)

    def get_last(self) -> str:
        return self._read_iterations[-1]

    def replace_last(self, data: str) -> None:
        self._read_iterations[-1] = data

    def next_bunch(self) -> None:
        self._read_iterations.append("")

    def get_value(self) -> str:
        return "".join(self._read_iterations)

    def __str__(self):
        return self.get_value()


class Reader(object):
    def __init__(self, session: "Session"):
        self.session = session

    def read_iterator(self):
        retries_count = 0
        while (self.session.config.max_loop_retries == 0 or
               retries_count < self.session.config.max_loop_retries):
            data = receive_all(self.session, self.session.config.timeout)
            if data:
                data = normalize_buffer(data)
                logger.debug(data)
                yield data
                retries_count = 0
            else:
                retries_count += 1
                time.sleep(self.session.config.empty_loop_timeout)

        raise SessionLoopLimitException(
            "Session Loop limit exceeded, {} loops".format(retries_count),
        )
