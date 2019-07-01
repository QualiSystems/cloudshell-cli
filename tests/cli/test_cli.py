# from unittest import TestCase
#
# # from mock import MagicMock as Mock
# import mock
# from cloudshell.cli.service.cli import CLI
#
#
# class TestCli(TestCase):
#     def setUp(self):
#         self._cli = CLI(mock.MagicMock())
#
#     @mock.patch('cloudshell.cli.service.session_pool_context_manager.SessionPoolContextManager')
#     def test_create_instance(self, context_manager):
#         with self._cli.get_session(mock.Mock(), mock.Mock(), mock.Mock()) as session:
#             pass
#
#         context_manager.assert_called_once()
