from __future__ import annotations

from unittest.mock import Mock

import pytest

from cloudshell.cli.configurator import CLIServiceConfigurator
from cloudshell.cli.factory.session_factory import GenericSessionFactory


@pytest.fixture
def registered_sessions():
    return [
        GenericSessionFactory(Mock(SESSION_TYPE="ssh", name="ssh")),
        GenericSessionFactory(Mock(SESSION_TYPE="telnet", name="telnet")),
        GenericSessionFactory(Mock(SESSION_TYPE="console", name="console")),
        GenericSessionFactory(Mock(SESSION_TYPE="ssh", name="ssh2")),
    ]


def test_get_supported_sessions_auto(registered_sessions, logger):
    cli_configurator = CLIServiceConfigurator(
        "Auto", "host", logger, registered_sessions=registered_sessions
    )

    assert cli_configurator._supported_sessions == tuple(registered_sessions)


def test_get_supported_sessions_ssh(registered_sessions, logger):
    cli_configurator = CLIServiceConfigurator(
        "SSH", "host", logger, registered_sessions=registered_sessions
    )

    assert cli_configurator._supported_sessions == (
        registered_sessions[0],
        registered_sessions[3],
    )


def test_get_supported_sessions_telnet(registered_sessions, logger):
    cli_configurator = CLIServiceConfigurator(
        "Telnet", "host", logger, registered_sessions=registered_sessions
    )

    assert cli_configurator._supported_sessions == (registered_sessions[1],)


def test_get_supported_sessions_console(registered_sessions, logger):
    cli_configurator = CLIServiceConfigurator(
        "Console", "host", logger, registered_sessions=registered_sessions
    )

    assert cli_configurator._supported_sessions == (registered_sessions[2],)
