import re
from typing import TYPE_CHECKING
from cloudshell.cli.session.exception import PromCannotBeDefinedException
from cloudshell.cli.session.helper.send_receive import clear_buffer, send_line, receive_all
from cloudshell.cli.session.prompt.prompt import Prompt

if TYPE_CHECKING:
    from cloudshell.cli.session.core.session import Session


class BasicPromptFactory(object):

    @staticmethod
    def create_prompt(session: "Session", command: str):
        clear_buffer(session)
        send_line(session, command or "")
        data = receive_all(session, 2)

        if data:
            return Prompt(re.split(r"\n", data.strip())[-1], data)
        else:
            raise PromCannotBeDefinedException("No output for prompt")
