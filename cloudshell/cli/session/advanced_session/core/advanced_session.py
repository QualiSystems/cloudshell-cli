from abc import ABCMeta, abstractmethod
from threading import RLock
from typing import TYPE_CHECKING

from cloudshell.cli.session.advanced_session.actions.action_map import ActionMap
from cloudshell.cli.session.advanced_session.actions.exceptions import ActionsReturnData
from cloudshell.cli.session.advanced_session.actions.validators.action_loop_detector import ActionLoopDetector
from cloudshell.cli.session.advanced_session.core.advanced_config import AdvancedSessionConfig
from cloudshell.cli.session.advanced_session.core.session_reader import Reader, SessionBuffer
from cloudshell.cli.session.advanced_session.exceptions import AdvancedSessionException
from cloudshell.cli.session.advanced_session.helper.reader_helper import remove_command
from cloudshell.cli.session.basic_session.helper.send_receive import clear_buffer, send_line

ABC = ABCMeta("ABC", (object,), {"__slots__": ()})

if TYPE_CHECKING:
    from logging import Logger
    from cloudshell.cli.session.advanced_session.core.entities import Command
    from cloudshell.cli.session.basic_session.core.session import BasicSession
    from cloudshell.cli.session.basic_session.prompt.prompt import AbstractPrompt


class AbstractAdvancedSession(ABC):

    @abstractmethod
    def send(self, command):
        raise NotImplementedError

    @abstractmethod
    def expect(self, prompt, command, action_map):
        raise NotImplementedError

    def send_command(self, command):
        """
        :param cloudshell.cli.session.advanced_session.model.session_command.Command command:
        :rtype: cloudshell.cli.session.advanced_session.model.command_response.CommandResponse
        """
        raise NotImplementedError


class AdvancedSession(AbstractAdvancedSession):

    def __init__(self, session: "BasicSession", logger: "Logger", session_config: AdvancedSessionConfig = None):
        self.session = session
        self.logger = logger
        self._session_config = session_config or AdvancedSessionConfig()
        self.lock = RLock()

    def _get_reader(self):
        return Reader(
            logger=self.logger,
            session=self.session
        )

    def _get_action_loop_detector(self):
        if self._session_config.loop_detector:
            return ActionLoopDetector(
                self._session_config.loop_detector_max_action_loops,
                self._session_config.loop_detector_max_combination_length
            )

    def send(self, command: str):
        if command is not None:
            clear_buffer(self.session, self.session.config.clear_buffer_timeout)

            self.logger.debug("Command: {}".format(command))
            send_line(self.session, command)

    def expect(self, prompt: "AbstractPrompt", command: str, action_map: ActionMap):

        if not prompt:
            raise AdvancedSessionException("Prompt is not defined")

        if not action_map:
            action_map = ActionMap()

            buffer = SessionBuffer()

            is_correct_exit = False

            action_loop_detector = self._get_action_loop_detector()

            for data in self._get_reader().read_iterator():
                buffer.append_last(data)
                if self._session_config.remove_command:
                    remove_command(buffer, command)
                if prompt.match(buffer.get_last()):
                    is_correct_exit = True

                try:
                    if action_map.process(session=self,
                                          logger=self.logger,
                                          output=buffer.get_last(),
                                          action_loop_detector=action_loop_detector):
                        buffer.next_bunch()
                except (ActionsReturnData,):
                    # Normal exit
                    is_correct_exit = True

                if is_correct_exit:
                    return buffer.get_value()

    def send_command(self, command: "Command"):
        if self._session_config.use_exact_prompt:
            if command.prompt and command.prompt != self.session.get_prompt():
                raise AdvancedSessionException("Command prompt is not matched with the session prompt")
            prompt = self.session.get_prompt()
        else:
            prompt = command.prompt or self.session.get_prompt()

        with self.lock:
            self.send(command.command)
            return self.expect(prompt, command.command, command.action_map)
