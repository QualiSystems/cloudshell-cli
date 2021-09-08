import logging
from functools import lru_cache
from threading import RLock
from typing import TYPE_CHECKING, Optional, Iterator

from cloudshell.cli.session.helper.send_receive import clear_buffer, send_line
from cloudshell.cli.process.actions.action_map import ActionMap
from cloudshell.cli.process.actions.exceptions import ActionsReturnData
from cloudshell.cli.process.command.entities import CommandResponse
from cloudshell.cli.process.actions.validators.action_loop_detector import ActionLoopDetector
from cloudshell.cli.process.command.config import ProcessingConfig
from cloudshell.cli.process.command.reader import Reader, ResponseBuffer
from cloudshell.cli.process.exceptions import SessionProcessingException
from cloudshell.cli.process.helper.reader_helper import remove_command

if TYPE_CHECKING:
    from cloudshell.cli.process.command.entities import Command
    from cloudshell.cli.session.core.session import Session
    from cloudshell.cli.session.prompt.prompt import Prompt

logger = logging.getLogger(__name__)


class CommandProcessor(object):

    def __init__(self, session: "Session", processing_config: ProcessingConfig = None):
        self.session = session
        self._config = processing_config or ProcessingConfig()
        self.lock = RLock()

    @property
    @lru_cache()
    def _session_read_iterator(self) -> Iterator[str]:
        return Reader(
            session=self.session
        ).read_iterator()

    def _get_action_loop_detector(self) -> ActionLoopDetector:
        return ActionLoopDetector(
            self._config.loop_detector_max_action_loops,
            self._config.loop_detector_max_combination_length
        )

    def send(self, command: "Command") -> None:
        if command.clear_buffer:
            clear_buffer(self.session, self.session.config.clear_buffer_timeout)

        logger.debug("Command: {}".format(command))
        send_line(self.session, command.command)

    def expect(self, command: "Command", prompt: Optional["Prompt"] = None) -> "CommandResponse":

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
                buffer.append_last(next(self._session_read_iterator))
            except Exception as e:
                if action_map.process_exception(session=self.session,
                                                logger=logger,
                                                output=buffer.get_last(),
                                                action_loop_detector=action_loop_detector,
                                                exception=e):
                    # buffer.next_bunch()
                    continue
                else:
                    raise e

            if self._config.remove_command:
                remove_command(buffer, command.command)

            if prompt.match(buffer.get_last()):
                is_correct_exit = True

            try:
                if action_map.process(session=self.session,
                                      logger=logger,
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
        if self._config.use_exact_prompt:
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

    def switch_prompt(self, command: "Command") -> "Prompt":
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
                    buffer.append_last(next(self._session_read_iterator))
                except Exception as e:
                    if action_map.process_exception(session=self.session,
                                                    logger=logger,
                                                    output=buffer.get_last(),
                                                    action_loop_detector=action_loop_detector,
                                                    exception=e):
                        # buffer.next_bunch()
                        continue

                if action_map.process(session=self.session,
                                      logger=logger,
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
