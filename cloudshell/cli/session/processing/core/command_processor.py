from abc import ABCMeta, abstractmethod
from functools import lru_cache
from threading import RLock
from typing import TYPE_CHECKING, Optional

from cloudshell.cli.session.basic_session.helper.send_receive import clear_buffer, send_line
from cloudshell.cli.session.processing.actions.action_map import ActionMap
from cloudshell.cli.session.processing.actions.exceptions import ActionsReturnData
from cloudshell.cli.session.processing.actions.validators.action_loop_detector import ActionLoopDetector
from cloudshell.cli.session.processing.core.config import ProcessingConfig
from cloudshell.cli.session.processing.core.reader import Reader, ResponseBuffer
from cloudshell.cli.session.processing.exceptions import SessionProcessingException
from cloudshell.cli.session.processing.helper.reader_helper import remove_command

ABC = ABCMeta("ABC", (object,), {"__slots__": ()})

if TYPE_CHECKING:
    from logging import Logger
    from cloudshell.cli.session.processing.core.entities import Command, CommandResponse
    from cloudshell.cli.session.basic_session.core.session import AbstractSession
    from cloudshell.cli.session.basic_session.prompt.prompt import AbstractPrompt


class AbstractCommandProcessor(ABC):

    @abstractmethod
    def send(self, command: "Command") -> None:
        raise NotImplementedError

    @abstractmethod
    def expect(self, command: "Command", prompt: "AbstractPrompt") -> "CommandResponse":
        raise NotImplementedError

    def send_command(self, command: "Command") -> "CommandResponse":
        raise NotImplementedError

    def switch_prompt(self, command: "Command") -> "AbstractPrompt":
        raise NotImplementedError


class CommandProcessor(AbstractCommandProcessor):

    def __init__(self, session: "AbstractSession", logger: "Logger", processing_config: ProcessingConfig = None):
        self.session = session
        self.logger = logger
        self._processing_config = processing_config or ProcessingConfig()
        self.lock = RLock()

    @lru_cache()
    def _session_reader(self) -> Reader:
        return Reader(
            logger=self.logger,
            session=self.session
        )

    def _get_action_loop_detector(self) -> ActionLoopDetector:
        return ActionLoopDetector(
            self._processing_config.loop_detector_max_action_loops,
            self._processing_config.loop_detector_max_combination_length
        )

    def send(self, command: "Command") -> None:
        if command.clear_buffer:
            clear_buffer(self.session, self.session.config.clear_buffer_timeout)

        self.logger.debug("Command: {}".format(command))
        send_line(self.session, command.command)

    def expect(self, command: "Command", prompt: Optional["AbstractPrompt"] = None) -> "CommandResponse":

        prompt = prompt or command.prompt

        if not prompt:
            raise SessionProcessingException("Prompt is not defined")

        action_map = command.action_map or ActionMap()

        buffer = ResponseBuffer()

        is_correct_exit = False

        action_loop_detector = None

        if command.detect_loops:
            action_loop_detector = self._get_action_loop_detector()

        while True:
            try:
                buffer.append_last(next(self._session_reader().read_iterator()))
            except Exception as e:
                if action_map.process_exception(session=self.session,
                                                logger=self.logger,
                                                output=buffer.get_last(),
                                                action_loop_detector=action_loop_detector,
                                                exception=e):
                    # buffer.next_bunch()
                    continue
                else:
                    raise e

            if self._processing_config.remove_command:
                remove_command(buffer, command.command)

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
                return CommandResponse(buffer)

    def _reconcile_prompt(self, command: "Command"):
        """Reconcile command prompt, if present, with session prompt"""
        if self._processing_config.use_exact_prompt:
            if command.prompt and command.prompt != self.session.get_prompt():
                raise SessionProcessingException("Command prompt is not matched with the session prompt")
            prompt = self.session.get_prompt()
        else:
            prompt = command.prompt or self.session.get_prompt()
        return prompt

    def send_command(self, command: "Command") -> "CommandResponse":
        with self.lock:
            if not self.session.get_active():
                raise SessionProcessingException("Session is not active")

            prompt = self._reconcile_prompt(command)

            self.send(command)
            return self.expect(command, prompt)

    def switch_prompt(self, command: "Command") -> "AbstractPrompt":
        with self.lock:
            if not self.session.get_active():
                raise SessionProcessingException("Session is not active")

            self.send(command)

            prompt = command.prompt
            action_map = command.action_map or ActionMap()
            buffer = ResponseBuffer()
            action_loop_detector = None

            if command.detect_loops:
                action_loop_detector = self._get_action_loop_detector()

            self.session.discard_current_prompt()

            while True:
                try:
                    buffer.append_last(next(self._session_reader().read_iterator()))
                except Exception as e:
                    if action_map.process_exception(session=self.session,
                                                    logger=self.logger,
                                                    output=buffer.get_last(),
                                                    action_loop_detector=action_loop_detector,
                                                    exception=e):
                        # buffer.next_bunch()
                        continue

                if action_map.process(session=self.session,
                                      logger=self.logger,
                                      output=buffer.get_last(),
                                      action_loop_detector=action_loop_detector):
                    buffer.next_bunch()
                    continue

                if prompt:
                    if prompt.match(buffer.get_last()):
                        return self.session.get_prompt()
                    continue

                prompt = self.session.get_prompt()
                if prompt:
                    return prompt
