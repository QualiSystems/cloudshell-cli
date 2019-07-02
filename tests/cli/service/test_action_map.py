import unittest
from unittest import mock

from cloudshell.cli.service.action_map import Action
from cloudshell.cli.service.action_map import ActionMap


class TestAction(unittest.TestCase):
    def setUp(self):
        self.session = mock.MagicMock()
        self.logger = mock.MagicMock()
        self.callback = mock.MagicMock()
        self.action = Action(pattern="test pattern", callback=self.callback)

    def test_call(self):
        """Check that method will call callback function with session and logger as attributes"""
        # act
        self.action(session=self.session, logger=self.logger)
        # verify
        self.callback.assert_called_once_with(self.session, self.logger)

    @mock.patch("cloudshell.cli.service.action_map.re")
    def test_match_return_true(self, re):
        """Check that method will return True if output matches pattern"""
        re.search.return_value = True
        output = "test output"
        # act
        result = self.action.match(output)
        # verify
        self.assertTrue(result)

    @mock.patch("cloudshell.cli.service.action_map.re")
    def test_match_return_false(self, re):
        """Check that method will return False if output doesn't match pattern"""
        re.search.return_value = False
        output = "test output"
        # act
        result = self.action.match(output)
        # verify
        self.assertFalse(result)


class TestActionMap(unittest.TestCase):
    def setUp(self):
        self.session = mock.MagicMock()
        self.logger = mock.MagicMock()
        self.callback = mock.MagicMock()
        self.actions = [Action(pattern="[Pp]attern 1", callback=self.callback),
                        Action(pattern="[Pp]attern 2", callback=self.callback, execute_once=True),
                        Action(pattern="[Pp]attern 3", callback=self.callback, execute_once=True)]

        self.action_map = ActionMap(actions=self.actions)

    def test_actions(self):
        """Check that method will return all actions"""
        action1, action2, action3 = self.actions
        self.action_map.matched_patterns = {action1.pattern, action2.pattern}
        # verify
        self.assertEqual(self.action_map.actions, [action1, action2, action3])

    def test_active_actions(self):
        """Check that method will return only active actions"""
        action1, action2, action3 = self.actions
        self.action_map.matched_patterns = {action1.pattern, action2.pattern}
        # verify
        self.assertEqual(self.action_map.active_actions, [action1, action3])

    def test_extend(self):
        """Check that extend will add new actions and will not override existing one"""
        default_actions = [Action(pattern="[Pp]attern 4", callback=self.callback),
                           Action(pattern="[Pp]attern 2", callback=self.callback)]

        default_action_map = ActionMap(actions=default_actions)

        default_action1, default_action2 = default_actions
        action1, action2, action3 = self.actions

        default_action_map.matched_patterns = {default_action1.pattern, default_action2.pattern}
        self.action_map.matched_patterns = {action3.pattern}

        # act
        self.action_map.extend(action_map=default_action_map)

        # verify
        self.assertEqual(self.action_map.matched_patterns, {default_action1.pattern,
                                                            default_action2.pattern,
                                                            action3.pattern})

        self.assertEqual(self.action_map.actions, [action1, action2, action3, default_action1])

    def test_extend_with_override_true(self):
        """Check that extend will add new actions and will not override existing one"""
        default_actions = [Action(pattern="[Pp]attern 4", callback=self.callback),
                           Action(pattern="[Pp]attern 2", callback=self.callback)]

        default_action_map = ActionMap(actions=default_actions)

        default_action1, default_action2 = default_actions
        action1, action2, action3 = self.actions

        default_action_map.matched_patterns = {default_action1.pattern, default_action2.pattern}
        self.action_map.matched_patterns = {action3.pattern}

        # act
        self.action_map.extend(action_map=default_action_map, override=True)

        # verify
        self.assertEqual(self.action_map.matched_patterns, {default_action1.pattern,
                                                            default_action2.pattern,
                                                            action3.pattern})

        self.assertEqual(self.action_map.actions, [action1, default_action2, action3, default_action1])

    def test_add(self):
        """Check that __add__ method will create new ActionMap"""
        default_actions = [Action(pattern="[Pp]attern 4", callback=self.callback),
                           Action(pattern="[Pp]attern 2", callback=self.callback)]

        default_action_map = ActionMap(actions=default_actions)

        default_action1, default_action2 = default_actions
        action1, action2, action3 = self.actions

        default_action_map.matched_patterns = {default_action1.pattern, default_action2.pattern}
        self.action_map.matched_patterns = {action3.pattern}

        # act
        result = self.action_map + default_action_map

        # verify
        self.assertEqual(result.matched_patterns, set())
        self.assertEqual(result.actions, [action1, action2, action3, default_action1])
