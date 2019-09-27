from collections import OrderedDict
from unittest import TestCase

from cloudshell.cli.session.expect_session import ActionLoopDetector, ExpectSession
from cloudshell.cli.session.session_exceptions import (
    CommandExecutionException,
    ExpectedSessionException,
    SessionLoopLimitException,
    SessionReadTimeout,
)

try:
    from unittest.mock import MagicMock, Mock, call, patch
except ImportError:
    from mock import MagicMock, Mock, call, patch


class TestExpectSessionException(Exception):
    pass


class ExpectSessionImpl(ExpectSession):
    def _initialize_session(self, prompt, logger):
        pass

    def _connect_actions(self, prompt, logger):
        pass

    def connect(self, prompt, logger):
        pass

    def disconnect(self):
        pass

    def _receive(self, timeout, logger):
        pass

    def _send(self, command, logger):
        pass


@patch(
    "cloudshell.cli.session.expect_session.ActionLoopDetector.loops_detected",
    return_value=False,
)
@patch("cloudshell.cli.session.expect_session.normalize_buffer")
class TestExpectSession(TestCase):
    def setUp(self):
        self._logger = Mock()
        self._connect = Mock()
        self._disconnect = Mock()
        self._send = Mock()
        self._receive = Mock()
        self._instance = ExpectSessionImpl()
        self._instance._send = self._send
        self._instance._receive = self._receive
        self._instance.connect = self._connect
        self._instance.disconnect = self._disconnect

    def test_init_attributes(self, normalize_buffer, loops_detected):
        mandatory_attributes = [
            "_loop_detector_max_combination_length",
            "_empty_loop_timeout",
            "_clear_buffer_timeout",
            "_reconnect_timeout",
            "_active",
            "_loop_detector_max_action_loops",
            "_max_loop_retries",
            "_timeout",
            "_new_line",
        ]
        self.assertEqual(
            len(
                set(mandatory_attributes).difference(
                    set(self._instance.__dict__.keys())
                )
            ),
            0,
        )

    def test_session_type(self, normalize_buffer, loops_detected):
        self.assertEqual(self._instance.session_type, "EXPECT")

    def test_active(self, normalize_buffer, loops_detected):
        self.assertFalse(self._instance.active())

    def test_clear_buffer_receive_call(self, normalize_buffer, loops_detected):
        timeout = Mock()
        self._receive.side_effect = SessionReadTimeout()
        self._instance._clear_buffer(timeout, self._logger)
        self._receive.assert_called_once_with(timeout, self._logger)

    def test_clear_buffer_raise_exception(self, normalize_buffer, loops_detected):
        exception = Exception
        self._receive.side_effect = exception()
        timeout = Mock()
        with self.assertRaises(exception):
            self._instance._clear_buffer(timeout, self._logger)

    def test_clear_buffer_exit_with_no_data(self, normalize_buffer, loops_detected):
        self._receive.side_effect = ["", TestExpectSessionException("Breaking loop")]
        timeout = Mock()
        self._instance._clear_buffer(timeout, self._logger)
        self.assertTrue(True)

    def test_clear_buffer_exit_on_second_attempt(
        self, normalize_buffer, loops_detected
    ):
        self._receive.side_effect = [
            "test",
            "",
            TestExpectSessionException("Breaking loop"),
        ]
        timeout = Mock()
        self._instance._clear_buffer(timeout, self._logger)
        mock_calls = [call(timeout, self._logger), call(timeout, self._logger)]
        self._receive.assert_has_calls(mock_calls)

    def test_send_line(self, normalize_buffer, loops_detected):
        command = "test"
        self._instance.send_line(command, self._logger)
        self._send.assert_called_once_with(
            command + self._instance._new_line, self._logger
        )

    def test_receive_all_exit_by_timeout(self, normalize_buffer, loops_detected):
        self._receive.side_effect = SessionReadTimeout()
        exception = ExpectedSessionException
        with self.assertRaises(exception):
            self._instance._receive_all(0.1, self._logger)

    def test_receive_all_receive_call(self, normalize_buffer, loops_detected):
        self._receive.side_effect = ["test", SessionReadTimeout()]
        self._instance._receive_all(2, self._logger)
        mock_calls = [call(0.1, self._logger), call(0.1, self._logger)]
        self._receive.assert_has_calls(mock_calls)

    def test_receive_get_all_data(self, normalize_buffer, loops_detected):
        data1 = "test"
        data2 = "tesst"
        self._receive.side_effect = [data1, data2, SessionReadTimeout()]
        result = self._instance._receive_all(2, self._logger)
        self.assertTrue(result and result == data1 + data2)

    @patch("cloudshell.cli.session.expect_session.ExpectSession.send_line")
    @patch("cloudshell.cli.session.expect_session.ExpectSession._receive_all")
    @patch("cloudshell.cli.session.expect_session.ExpectSession._clear_buffer")
    def test_hardware_expect_clear_buffer_calls(
        self, clear_buffer, receive_all, send_line, normalize_buffer, loops_detected
    ):
        command = "test_command"
        expected_string = "test_string"
        receive_all.return_value = expected_string
        normalize_buffer.return_value = expected_string
        self._instance.hardware_expect(command, expected_string, self._logger)
        mock_calls = [
            call(self._instance._clear_buffer_timeout, self._logger),
            call(self._instance._clear_buffer_timeout, self._logger),
        ]
        clear_buffer.assert_has_calls(mock_calls)

    @patch("cloudshell.cli.session.expect_session.ExpectSession.send_line")
    @patch("cloudshell.cli.session.expect_session.ExpectSession._receive_all")
    @patch("cloudshell.cli.session.expect_session.ExpectSession._clear_buffer")
    def test_hardware_expect_send_line_call(
        self, clear_buffer, receive_all, send_line, normalize_buffer, loops_detected
    ):
        command = "test_command"
        expected_string = "test_string"
        receive_all.return_value = expected_string
        normalize_buffer.return_value = expected_string
        self._instance.hardware_expect(command, expected_string, self._logger)
        send_line.assert_called_once_with(command, self._logger)

    @patch("cloudshell.cli.session.expect_session.ExpectSession.send_line")
    @patch("cloudshell.cli.session.expect_session.ExpectSession._receive_all")
    @patch("cloudshell.cli.session.expect_session.ExpectSession._clear_buffer")
    def test_hardware_expect_empty_expected_string(
        self, clear_buffer, receive_all, send_line, normalize_buffer, loops_detected
    ):
        command = "test_command"
        expected_string = None
        receive_all.return_value = expected_string
        normalize_buffer.return_value = expected_string
        exception = ExpectedSessionException
        with self.assertRaises(exception):
            self._instance.hardware_expect(command, expected_string, self._logger)

    @patch("cloudshell.cli.session.expect_session.ExpectSession.send_line")
    @patch("cloudshell.cli.session.expect_session.ExpectSession._receive_all")
    @patch("cloudshell.cli.session.expect_session.ExpectSession._clear_buffer")
    def test_hardware_expect_raise_session_loop_limit_exceded(
        self, clear_buffer, receive_all, send_line, normalize_buffer, loops_detected
    ):
        command = "test_command"
        expected_string = "test_string"
        side_efect = [command, "", "", ""]
        receive_all.side_effect = side_efect
        normalize_buffer.side_effect = side_efect
        exception = SessionLoopLimitException
        retries = 2
        with self.assertRaises(exception):
            self._instance.hardware_expect(
                command, expected_string, self._logger, retries=retries
            )

    @patch("cloudshell.cli.session.expect_session.ExpectSession.send_line")
    @patch("cloudshell.cli.session.expect_session.ExpectSession._receive_all")
    @patch("cloudshell.cli.session.expect_session.ExpectSession._clear_buffer")
    def test_hardware_expect_receive_all_call(
        self, clear_buffer, receive_all, send_line, normalize_buffer, loops_detected
    ):
        command = "test_command"
        expected_string = "test_string"
        receive_all.return_value = expected_string
        normalize_buffer.return_value = expected_string
        timeout = Mock()
        self._instance.hardware_expect(
            command, expected_string, self._logger, timeout=timeout
        )
        receive_all.assrrt_called_once_with(timeout, self._logger)

    @patch("cloudshell.cli.session.expect_session.ExpectSession.send_line")
    @patch("cloudshell.cli.session.expect_session.ExpectSession._receive_all")
    @patch("cloudshell.cli.session.expect_session.ExpectSession._clear_buffer")
    def test_hardware_expect_normalize_buffer_call(
        self, clear_buffer, receive_all, send_line, normalize_buffer, loops_detected
    ):
        command = "test_command"
        expected_string = "test_string"
        receive_all.return_value = expected_string
        normalize_buffer.return_value = expected_string
        timeout = Mock()
        self._instance.hardware_expect(
            command, expected_string, self._logger, timeout=timeout
        )
        normalize_buffer.assrrt_called_once_with(expected_string)

    @patch("cloudshell.cli.session.expect_session.ExpectSession.send_line")
    @patch("cloudshell.cli.session.expect_session.ExpectSession._receive_all")
    @patch(
        "cloudshell.cli.session.expect_session.ExpectSession._clear_buffer",
        return_value="",
    )
    def test_hardware_expect_remove_command_from_output(
        self, clear_buffer, receive_all, send_line, normalize_buffer, loops_detected
    ):
        command = "test_command"
        expected_string = "test_string"
        out = """{0}
        {1}""".format(
            command, expected_string
        )
        receive_all.return_value = out
        normalize_buffer.return_value = out
        timeout = Mock()
        result = self._instance.hardware_expect(
            command, expected_string, self._logger, timeout=timeout
        )
        self.assertEqual(result.strip(), expected_string)

    @patch("cloudshell.cli.session.expect_session.ExpectSession.send_line")
    @patch("cloudshell.cli.session.expect_session.ExpectSession._receive_all")
    @patch(
        "cloudshell.cli.session.expect_session.ExpectSession._clear_buffer",
        return_value="",
    )
    def test_hardware_expect_action_map_call(
        self, clear_buffer, receive_all, send_line, normalize_buffer, loops_detected
    ):
        command = "test_command"
        fake_out = "test_test"
        expected_string = "test_string"
        side_effect = [fake_out, expected_string]
        receive_all.side_effect = side_effect
        normalize_buffer.side_effect = side_effect
        test_func = Mock()
        action_map = OrderedDict({fake_out: test_func})
        self._instance.hardware_expect(
            command, expected_string, self._logger, action_map=action_map
        )
        test_func.assert_called_once_with(self._instance, self._logger)

    @patch("cloudshell.cli.session.expect_session.ExpectSession.send_line")
    @patch("cloudshell.cli.session.expect_session.ExpectSession._receive_all")
    @patch(
        "cloudshell.cli.session.expect_session.ExpectSession._clear_buffer",
        return_value="",
    )
    def test_hardware_expect_error_map_call(
        self, clear_buffer, receive_all, send_line, normalize_buffer, loops_detected
    ):
        command = "test_command"
        expected_string = "test_string"
        receive_all.return_value = expected_string
        normalize_buffer.return_value = expected_string
        error_map = OrderedDict({expected_string: "test_error"})
        exception = CommandExecutionException
        with self.assertRaises(exception):
            self._instance.hardware_expect(
                command, expected_string, self._logger, error_map=error_map
            )

    @patch("cloudshell.cli.session.expect_session.ExpectSession.send_line", MagicMock())
    @patch("cloudshell.cli.session.expect_session.ExpectSession._receive_all")
    @patch(
        "cloudshell.cli.session.expect_session.ExpectSession._clear_buffer",
        MagicMock(return_value=""),
    )
    def test_hardware_expect_error_map_call_with_exception(
        self, receive_all, normalize_buffer, loops_detected
    ):
        class TestException(CommandExecutionException):
            pass

        command = "test_command"
        expected_string = "test_string"
        receive_all.return_value = expected_string
        normalize_buffer.return_value = expected_string
        error_map = OrderedDict({expected_string: TestException("test_error")})
        with self.assertRaises(TestException):
            self._instance.hardware_expect(
                command, expected_string, self._logger, error_map=error_map
            )

    def test_reconnect_disconnect_call(self, normalize_buffer, loops_detected):
        prompt = Mock()
        self._instance.reconnect(prompt, self._logger)
        self._disconnect.assert_called_once_with()

    def test_reconnect_connect_call(self, normalize_buffer, loops_detected):
        prompt = Mock()
        self._instance.reconnect(prompt, self._logger)
        self._connect.assert_called_once_with(prompt, self._logger)

    def test_reconnect_raise_timeout_exception(self, normalize_buffer, loops_detected):
        prompt = Mock()
        exception = ExpectedSessionException
        self._connect.side_effect = Exception()
        with self.assertRaises(exception):
            self._instance.reconnect(prompt, self._logger, timeout=0.1)


class TestActionLoopDetector(TestCase):
    def setUp(self):
        self._max_loops = 2
        self._max_combination_length = 2
        self._instance = ActionLoopDetector(
            self._max_loops, self._max_combination_length
        )

    def test_detect_simple_loop(self):
        key_sequence = ["test_key1", "test_key2", "test_key1", "test_key2"]
        loop_detected = False
        for key in key_sequence:
            if self._instance.loops_detected(key):
                loop_detected = True
        self.assertTrue(loop_detected)

    def test_no_loop(self):
        key_sequence = ["test_key1", "test_key2", "test_key1", "test_key3"]
        loop_detected = False
        for key in key_sequence:
            if self._instance.loops_detected(key):
                loop_detected = True
        self.assertFalse(loop_detected)
