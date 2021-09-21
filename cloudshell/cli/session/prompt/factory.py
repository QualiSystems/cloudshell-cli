import logging
import re
from typing import TYPE_CHECKING, Optional
from cloudshell.cli.session.helper.send_receive import clear_buffer, send_line, receive_all
from cloudshell.cli.session.prompt.exception import PromCannotBeDefinedException, PromptException
from cloudshell.cli.session.prompt.prompt import Prompt

if TYPE_CHECKING:
    from cloudshell.cli.session.core.session import Session

logger = logging.getLogger(__name__)


class BasicPromptFactory(object):

    def create_prompt(self, session: "Session", command: Optional["str"]) -> Prompt:
        clear_buffer(session)
        send_line(session, command or "")
        data = receive_all(session, session.config.prompt_timeout)

        pattern = "".join(data.strip().splitlines()[-2:]).strip()

        if pattern:
            prompt = Prompt(re.escape(pattern), data)
            self._validate_prompt(data, prompt)
            return prompt

        else:
            raise PromCannotBeDefinedException("Cannot identify prompt pattern")

    def _get_exact_pattern(self, data: str, prompt: Prompt) -> str:
        """Initialize exact pattern"""
        match = re.search(prompt.pattern, data, re.DOTALL)
        pattern = None
        if match.groups():
            pattern = match.group(1)

        if not pattern:
            logger.warning("Cannot match exact pattern.")
        return pattern

    def _validate_prompt(self, data: str, prompt: Prompt) -> None:

        if not prompt.match(data):
            raise PromptException("Exact prompt is not matching the output.")
