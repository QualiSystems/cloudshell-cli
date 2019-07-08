import unittest
from unittest import mock

from cloudshell.cli.service.error_map import Error
from cloudshell.cli.service.error_map import ErrorMap
from cloudshell.cli.session.session_exceptions import CommandExecutionException


class TestError(unittest.TestCase):
    def setUp(self):
        self.session = mock.MagicMock()
        self.logger = mock.MagicMock()
        self.error_msg = "error message"
        self.error = Error(pattern="test pattern", error=self.error_msg)

    def test_call(self):
        """Check that method will raise CommandExecutionException"""
        with self.assertRaisesRegex(CommandExecutionException, self.error_msg):
            self.error()

    def test_match_return_true(self):
        """Check that method will return True if output matches pattern"""
        output = "test pattern"
        # act
        result = self.error.match(output)
        # verify
        self.assertTrue(result)

    def test_match_return_false(self):
        """Check that method will return False if output doesn't match pattern"""
        output = "missed pattern"
        # act
        result = self.error.match(output)
        # verify
        self.assertFalse(result)


class TestErrorMap(unittest.TestCase):
    def setUp(self):
        self.logger = mock.MagicMock()
        self.errors = [Error(pattern="[Pp]attern 1", error="error 1"),
                       Error(pattern="[Pp]attern 2", error="error 2")]

        self.error_map = ErrorMap(errors=self.errors)

    def test_errors(self):
        """Check that method will return errors"""
        # verify
        self.assertEqual(self.error_map.errors, self.errors)

    def test_extend(self):
        """Check that extend will add new errors and will not override existing one"""
        default_error1 = Error(pattern="[Pp]attern 4", error="error 4")
        default_error2 = Error(pattern="[Pp]attern 2", error="error 2")
        default_error_map = ErrorMap(errors=[default_error1, default_error2])
        error1, error2 = self.errors
        # act
        self.error_map.extend(error_map=default_error_map)
        # verify
        self.assertEqual(self.error_map.errors, [error1, error2, default_error1])

    def test_extend_with_override_true(self):
        """Check that extend will add new errors and will not override existing one"""
        default_error1 = Error(pattern="[Pp]attern 4", error="error 4")
        default_error2 = Error(pattern="[Pp]attern 2", error="error 2")
        default_error_map = ErrorMap(errors=[default_error1, default_error2])
        error1, error2 = self.errors
        # act
        self.error_map.extend(error_map=default_error_map, override=True)
        # verify
        self.assertEqual(self.error_map.errors, [error1, default_error2, default_error1])

    def test_add(self):
        """Check that __add__ method will create new ErrorMap"""
        default_error1 = Error(pattern="[Pp]attern 4", error="error 4")
        default_error2 = Error(pattern="[Pp]attern 2", error="error 2")
        default_error_map = ErrorMap(errors=[default_error1, default_error2])
        error1, error2 = self.errors
        # act
        result = self.error_map + default_error_map
        # verify
        self.assertEqual(result.errors, [error1, error2, default_error1])

