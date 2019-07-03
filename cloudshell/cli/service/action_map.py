from collections import OrderedDict
import re


class Action(object):
    def __init__(self, pattern, callback, execute_once=False):
        """

        :param str pattern:
        :param function callback:
        :param bool execute_once:
        """
        self.pattern = pattern
        self.callback = callback
        self.execute_once = execute_once

    def __call__(self, session, logger):
        """

        :param cloudshell.cli.session.expect_session.ExpectSession session:
        :param logging.Logger logger:
        :return:
        """
        return self.callback(session, logger)

    def __repr__(self):
        """

        :rtype: str
        """
        return "{} pattern: {}, execute once: {}".format(super(Action, self).__repr__(),
                                                         self.pattern,
                                                         self.execute_once)

    def match(self, output):
        """

        :param str output:
        :rtype: bool
        """
        return bool(re.search(self.pattern, output, re.DOTALL))


class ActionMap(object):
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
        return [action for action in self._actions_dict.values()]

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

    def extend(self, action_map, override=False):
        """

        :param ActionMap action_map:
        :param bool override:
        :return:
        """
        for action in action_map.actions:
            if not override and action.pattern in self._actions_dict:
                continue
            self.add(action)

        self.matched_patterns |= action_map.matched_patterns

    def __call__(self, session, logger, output):
        """

        :param cloudshell.cli.session.expect_session.ExpectSession session:
        :param logging.Logger logger:
        :param str output:
        :return:
        """
        for action in self.active_actions:
            if action.match(output):
                self.matched_patterns.add(action.pattern)
                return action(session, logger)

    def __add__(self, other):
        """

        :param other:
        :rtype: ActionMap
        """
        if isinstance(other, type(self)):
            return ActionMap(actions=self.actions + other.actions)

        raise TypeError("unsupported operand type(s) for +: '{}' and '{}'".format(type(self), type(other)))

    def __repr__(self):
        """

        :rtype: str
        """
        return "{} matched patterns: {}, actions: {}".format(super(ActionMap, self).__repr__(),
                                                             self.matched_patterns,
                                                             self.actions)


# if __name__ == "__main__":
#     action_map1 = ActionMap(actions=[Action(pattern='action1', callback=lambda session, logger: session),
#                                      Action(pattern='action2', callback=lambda session, logger: session)])
#
#     action_map1.add(Action(pattern="action3",
#                            callback=lambda session, logger: session,
#                            execute_once=True))
#
#     action_map2 = ActionMap(actions=[Action(pattern='action10', callback=lambda session, logger: session),
#                                      Action(pattern='action20', callback=lambda session, logger: session)])
#
#     action_map2.add(Action(pattern="action1",
#                            callback=lambda session, logger: session,
#                            execute_once=True))
#
#     action_map2.extend(action_map1)
