import time
from typing import TYPE_CHECKING

from cloudshell.cli.session.advanced_session.exceptions import SessionLoopLimitException
from cloudshell.cli.session.advanced_session.helper.reader_helper import normalize_buffer
from cloudshell.cli.session.basic_session.helper.send_receive import receive_all

if TYPE_CHECKING:
    from logging import Logger
    from cloudshell.cli.session.basic_session.core.session import BasicSession


class SessionBuffer(object):
    def __init__(self):
        self._read_iterations = [""]
        self.command_removed = False

    def _validate(self, data: str):
        return normalize_buffer(data)

    def append_last(self, data: str):
        self._read_iterations[-1] += self._validate(data)

    def get_last(self):
        return self._read_iterations[-1]

    def replace_last(self, data: str):
        self._read_iterations[-1] = data

    def next_bunch(self):
        self._read_iterations.append("")

    def get_value(self):
        return "".join(self._read_iterations)

    # def set_value(self, data):
    #     self.data = data


class Reader(object):
    def __init__(self, logger: "Logger", session: "BasicSession"):
        self.session = session
        self.logger = logger

    def read_iterator(self):
        retries_count = 0
        while (self.session.config.max_loop_retries == 0 or
               retries_count < self.session.config.max_loop_retries):
            data = receive_all(self.session, self.session.config.timeout)
            if data:
                data = normalize_buffer(data)
                self.logger.debug(data)
                yield data
                retries_count = 0
            else:
                retries_count += 1
                time.sleep(self.session.config.empty_loop_timeout)

        raise SessionLoopLimitException(
            "Session Loop limit exceeded, {} loops".format(retries_count),
        )
