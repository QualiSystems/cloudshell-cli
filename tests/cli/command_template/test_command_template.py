from unittest import TestCase

from cloudshell.cli.command_template.command_template import CommandTemplate


class TestCommandModeContextManager(TestCase):
    def test_prepare_command(self):
        self.assertEqual(
            CommandTemplate("text[ text1 {arg1}]").prepare_command(), "text"
        )
        self.assertEqual(
            CommandTemplate("text[ text1{arg1}]").prepare_command(), "text"
        )
        self.assertEqual(
            CommandTemplate("text [text1 {arg1}]").prepare_command(), "text"
        )
        self.assertEqual(
            CommandTemplate("text [text1{arg1}]").prepare_command(), "text"
        )
        self.assertEqual(
            CommandTemplate("text[ text1 {arg1}]").prepare_command(arg1="test1"),
            "text text1 test1",
        )
        self.assertEqual(
            CommandTemplate("text[ text1{arg1}]").prepare_command(arg1="test1"),
            "text text1test1",
        )
        self.assertEqual(
            CommandTemplate("text [text1 {arg1}]").prepare_command(arg1="test1"),
            "text text1 test1",
        )
        self.assertEqual(
            CommandTemplate("text [text1{arg1}]").prepare_command(arg1="test1"),
            "text text1test1",
        )
        self.assertEqual(
            CommandTemplate("text[ text1 {arg1}][ text2 {arg2}]").prepare_command(),
            "text",
        )
        self.assertEqual(
            CommandTemplate("text [text1 {arg1}][ text2 {arg2}]").prepare_command(),
            "text",
        )
        self.assertEqual(
            CommandTemplate("text[ text1 {arg1}] [text2 {arg2}]").prepare_command(),
            "text",
        )
        self.assertEqual(
            CommandTemplate("text[ text1 {arg1}][ text2 {arg2}]").prepare_command(
                arg1="test1"
            ),
            "text text1 test1",
        )
        self.assertEqual(
            CommandTemplate("text [text1 {arg1}] [text2 {arg2}]").prepare_command(
                arg1="test1"
            ),
            "text text1 test1",
        )
        self.assertEqual(
            CommandTemplate("text[ text1 {arg1}][ text2 {arg2}]").prepare_command(
                arg2="test2"
            ),
            "text text2 test2",
        )
        self.assertEqual(
            CommandTemplate("text[ text1 {arg1}][ text2 {arg2}]").prepare_command(
                arg1="test1", arg2="test2"
            ),
            "text text1 test1 text2 test2",
        )
        self.assertEqual(
            CommandTemplate("text [text1 {arg1}] [text2 {arg2}]").prepare_command(
                arg1="test1", arg2="test2"
            ),
            "text text1 test1 text2 test2",
        )
