import logging
from collections import OrderedDict
import re
from typing import Callable, Optional, Type, TYPE_CHECKING

from cloudshell.cli.process.command.actions.exception import SessionLoopDetectorException

if TYPE_CHECKING:
    from cloudshell.cli.session.core.session import Session

logger = logging.getLogger(__name__)


class Action:
    def __init__(self, pattern: str, callback: Callable, execute_once: Optional[bool] = False):
        self.pattern = pattern
        self.compiled_pattern = re.compile(pattern=pattern, flags=re.DOTALL)
        self.callback = callback
        self.execute_once = execute_once

    def __call__(self, session: "Session"):
        return self.callback(session)

    def __repr__(self):
        """

        :rtype: str
        """
        return f"{super().__repr__()} pattern: {self.pattern}, execute once: {self.execute_once}"

    def match(self, output):
        """

        :param str output:
        :rtype: bool
        """
        return bool(self.compiled_pattern.search(output))


class ErrorAction(Action):
    def __init__(self, pattern: str, exception: Type[Exception], description: str):
        self._exception = exception
        self.description = description
        super(ErrorAction, self).__init__(pattern=pattern,
                                          callback=self.get_exception_callback(exception, description),
                                          execute_once=True)

    @staticmethod
    def get_exception_callback(exception: Type[Exception], description: str) -> Callable:
        def execute_exception():
            raise exception(description)

        return execute_exception


class ActionMap:
    def __init__(self, actions=None):
        """

        :param list[Action] actions:
        """
        if actions is None:
            actions = []

        self.matched_patterns = set()
        self._actions_dict = OrderedDict([(action.pattern, action) for action in actions])

    @property
    def actions(self):
        """

        :rtype: list[Action]
        """
        return list(self._actions_dict.values())

    @property
    def active_actions(self):
        """

        :rtype: list[Action]
        """
        return [action for action in self.actions if (not action.execute_once or
                                                      action.pattern not in self.matched_patterns)]

    def add(self, action):
        """

        :param Action action:
        :return:
        """
        self._actions_dict[action.pattern] = action

    def extend(self, action_map, override=False, extend_matched_patterns=True):
        """

        :param ActionMap action_map:
        :param bool override:
        :param bool extend_matched_patterns:
        :return:
        """
        for action in action_map.actions:
            if not override and action.pattern in self._actions_dict:
                continue
            self.add(action)

        if extend_matched_patterns:
            self.matched_patterns |= action_map.matched_patterns

    def process(self, session, output, action_loop_detector=None):
        """

        :param cloudshell.cli.session.expect_session.ExpectSession session:
        :param logging.Logger logger:
        :param str output:
        :param ActionLoopDetector action_loop_detector:
        :rtype: bool
        """
        for action in self.active_actions:
            if action.match(output):
                logger.debug(f"Matched Action with pattern: {action.pattern}")

                if action_loop_detector:
                    logger.debug(f"Checking loops for Action with pattern : {action.pattern}")

                    if action_loop_detector.loops_detected(action.pattern):
                        logger.error(f"Loops detected for action patter: {action.pattern}")
                        raise SessionLoopDetectorException("Expected actions loops detected")

                action(session)
                self.matched_patterns.add(action.pattern)
                return True

        return False

    def process_exception(self, session, logger, output, exception, action_loop_detector=None):
        pass

    def __add__(self, other):
        """

        :param other:
        :rtype: ActionMap
        """
        action_map_class = type(self)
        if isinstance(other, action_map_class):
            action_map = action_map_class(actions=self.actions)
            action_map.extend(other, extend_matched_patterns=False)
            return action_map

        raise TypeError(f"unsupported operand type(s) for +: '{type(self)}' and '{type(other)}'")

    def __repr__(self):
        """

        :rtype: str
        """
        return f"{super().__repr__()} matched patterns: {self.matched_patterns}, actions: {self.actions}"
