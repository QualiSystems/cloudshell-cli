from abc import ABCMeta, abstractmethod
from threading import RLock
from typing import TYPE_CHECKING

from cloudshell.cli.session.basic_session.helper.send_receive import clear_buffer, send_line
from cloudshell.cli.session.processing.actions.action_map import ActionMap
from cloudshell.cli.session.processing.actions.exceptions import ActionsReturnData
from cloudshell.cli.session.processing.actions.validators.action_loop_detector import ActionLoopDetector
from cloudshell.cli.session.processing.core.config import ProcessingConfig
from cloudshell.cli.session.processing.core.session_reader import Reader, OutputBuffer
from cloudshell.cli.session.processing.exceptions import SessionProcessingException
from cloudshell.cli.session.processing.helper.reader_helper import remove_command

ABC = ABCMeta("ABC", (object,), {"__slots__": ()})

if TYPE_CHECKING:
    from logging import Logger
    from cloudshell.cli.session.processing.core.entities import Command, CommandResponse
    from cloudshell.cli.session.basic_session.core.session import BasicSession
    from cloudshell.cli.session.basic_session.prompt.prompt import AbstractPrompt


class AbstractActionProcessor(ABC):

    @abstractmethod
    def send(self, command: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def expect(self, prompt: "AbstractPrompt", command: str, action_map: ActionMap) -> str:
        raise NotImplementedError

    def send_command(self, command: "Command") -> str:
        raise NotImplementedError


class ActionProcessor(AbstractActionProcessor):

    def __init__(self, session: "BasicSession", logger: "Logger", processing_config: ProcessingConfig = None):
        self.session = session
        self.logger = logger
        self._processing_config = processing_config or ProcessingConfig()
        self.lock = RLock()

    def _get_reader(self) -> Reader:
        return Reader(
            logger=self.logger,
            session=self.session
        )

    def _get_action_loop_detector(self) -> ActionLoopDetector:
        return ActionLoopDetector(
            self._processing_config.loop_detector_max_action_loops,
            self._processing_config.loop_detector_max_combination_length
        )

    def send(self, command: str) -> None:
        if command is not None:
            clear_buffer(self.session, self.session.config.clear_buffer_timeout)

            self.logger.debug("Command: {}".format(command))
            send_line(self.session, command)

    def expect(self, prompt: "AbstractPrompt", command: str, action_map: ActionMap, detect_loops=None) -> str:

        if not self.session.get_active():
            raise SessionProcessingException("Session is not active")

        if not prompt:
            raise SessionProcessingException("Prompt is not defined")

        if not action_map:
            action_map = ActionMap()

        buffer = OutputBuffer()

        is_correct_exit = False

        action_loop_detector = None

        if detect_loops:
            action_loop_detector = self._get_action_loop_detector()

        for data in self._get_reader().read_iterator():
            buffer.append_last(data)
            if self._processing_config.remove_command:
                remove_command(buffer, command)
            if prompt.match(buffer.get_last()):
                is_correct_exit = True

            try:
                if action_map.process(session=self.session,
                                      logger=self.logger,
                                      output=buffer.get_last(),
                                      action_loop_detector=action_loop_detector):
                    buffer.next_bunch()
            except (ActionsReturnData,):
                # Normal exit
                is_correct_exit = True

            if is_correct_exit:
                return buffer.get_value()

    def send_command(self, command: "Command") -> str:
        if self._processing_config.use_exact_prompt:
            if command.prompt and command.prompt != self.session.get_prompt():
                raise SessionProcessingException("Command prompt is not matched with the session prompt")
            prompt = self.session.get_prompt()
        else:
            prompt = command.prompt or self.session.get_prompt()

        with self.lock:
            self.send(command.command)
            return self.expect(prompt, command.command, command.action_map)
