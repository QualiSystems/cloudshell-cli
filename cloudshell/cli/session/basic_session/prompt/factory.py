import re
from typing import TYPE_CHECKING, Optional
from cloudshell.cli.session.basic_session.exceptions import PromCannotBeDefinedException
from cloudshell.cli.session.basic_session.helper.send_receive import clear_buffer, send_line, receive_all
from cloudshell.cli.session.basic_session.prompt.prompt import BasicPrompt

if TYPE_CHECKING:
    from cloudshell.cli.session.basic_session.core.session import BasicSession


class BasicPromptFactory(object):

    @staticmethod
    def create_prompt(session: "BasicSession", command: str):
        clear_buffer(session)
        send_line(session, command or "")
        data = receive_all(session, 2)

        if data:
            return BasicPrompt(re.split(r"\n", data.strip())[-1], data)
        else:
            raise PromCannotBeDefinedException("No output for prompt")
