import re
from collections import OrderedDict

from cloudshell.cli.session.session_exceptions import SessionLoopDetectorException


class Action:
    def __init__(self, pattern, callback, execute_once=False):
        """Initialize action.

        :param str pattern:
        :param function callback:
        :param bool execute_once:
        """
        self.pattern = pattern
        self.compiled_pattern = re.compile(pattern=pattern, flags=re.DOTALL)
        self.callback = callback
        self.execute_once = execute_once

    def __call__(self, session, logger):
        """Call.

        :param cloudshell.cli.session.expect_session.ExpectSession session:
        :param logging.Logger logger:
        :return:
        """
        return self.callback(session, logger)

    def __repr__(self):
        return (
            f"{super().__repr__()} pattern: {self.pattern}, "
            f"execute once: {self.execute_once}"
        )

    def match(self, output):
        """Match.

        :param str output:
        :rtype: bool
        """
        return bool(self.compiled_pattern.search(output))


class ActionMap:
    def __init__(self, actions=None):
        """Initialize Action Map.

        :param list[Action] actions:
        """
        if actions is None:
            actions = []

        self.matched_patterns = set()
        self._actions_dict = OrderedDict(
            [(action.pattern, action) for action in actions]
        )

    @property
    def actions(self):
        """Actions.

        :rtype: list[Action]
        """
        return list(self._actions_dict.values())

    @property
    def active_actions(self):
        """Active actions.

        :rtype: list[Action]
        """
        return [
            action
            for action in self.actions
            if (not action.execute_once or action.pattern not in self.matched_patterns)
        ]

    def add(self, action):
        """Add.

        :param Action action:
        :return:
        """
        self._actions_dict[action.pattern] = action

    def extend(self, action_map, override=False, extend_matched_patterns=True):
        """Extend.

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

    def process(
        self, session, logger, output, check_action_loop_detector, action_loop_detector
    ):
        """Process.

        :param cloudshell.cli.session.expect_session.ExpectSession session:
        :param logging.Logger logger:
        :param str output:
        :param bool check_action_loop_detector:
        :param ActionLoopDetector action_loop_detector:
        :rtype: bool
        """
        for action in self.active_actions:
            if action.match(output):
                logger.debug(f"Matched Action with pattern: {action.pattern}")

                if check_action_loop_detector:
                    logger.debug(
                        f"Checking loops for Action with pattern : {action.pattern}"
                    )

                    if action_loop_detector.loops_detected(action.pattern):
                        logger.error(
                            f"Loops detected for action patter: {action.pattern}"
                        )
                        raise SessionLoopDetectorException(
                            "Expected actions loops detected"
                        )

                action(session, logger)
                self.matched_patterns.add(action.pattern)
                return True

        return False

    def __add__(self, other):
        """Add.

        :param other:
        :rtype: ActionMap
        """
        action_map_class = type(self)
        if isinstance(other, action_map_class):
            action_map = action_map_class(actions=self.actions)
            action_map.extend(other, extend_matched_patterns=False)
            return action_map

        raise TypeError(
            f"unsupported operand type(s) for +: '{type(self)}' and '{type(other)}'"
        )

    def __repr__(self):
        return (
            f"{super().__repr__()} matched patterns: {self.matched_patterns}, "
            f"actions: {self.actions}"
        )


class ActionLoopDetector:
    """Help to detect loops for action combinations."""

    def __init__(self, max_loops, max_combination_length):
        """Initialize Action Loop Detector.

        :param max_loops:
        :param max_combination_length:
        :return:
        """
        self._max_action_loops = max_loops
        self._max_combination_length = max_combination_length
        self._action_history = []

    def loops_detected(self, action_pattern):
        """Add action key to the history and detect loops.

        :param str action_pattern:
        :return:
        """
        self._action_history.append(action_pattern)
        for combination_length in range(1, self._max_combination_length + 1):
            if self._is_combination_compatible(combination_length):
                if self._is_loop_exists(combination_length):
                    return True
        return False

    def _is_combination_compatible(self, combination_length):
        """Check if combinations may exist.

        :param combination_length:
        :return:
        """
        return len(self._action_history) / combination_length >= self._max_action_loops

    def _is_loop_exists(self, combination_length):
        """Detect loops for combination length.

        :param combination_length:
        :return:
        """
        reversed_history = self._action_history[::-1]
        combinations = [
            reversed_history[x : x + combination_length]
            for x in range(0, len(reversed_history), combination_length)
        ][: self._max_action_loops]
        for x, y in [combinations[x : x + 2] for x in range(0, len(combinations) - 1)]:
            if x != y:
                return False
        return True
