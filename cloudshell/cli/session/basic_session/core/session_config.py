from cloudshell.cli.session.basic_session.prompt.factory import BasicPromptFactory
from cloudshell.cli.session.basic_session.prompt.prompt import BasicPrompt


class SessionConfig(object):
    MAX_LOOP_RETRIES = 20
    READ_TIMEOUT = 30
    EMPTY_LOOP_TIMEOUT = 0.5
    CLEAR_BUFFER_TIMEOUT = 0.1

    def __init__(self, timeout=READ_TIMEOUT,
                 new_line="\r",
                 max_loop_retries=MAX_LOOP_RETRIES,
                 empty_loop_timeout=EMPTY_LOOP_TIMEOUT,
                 clear_buffer_timeout=CLEAR_BUFFER_TIMEOUT,
                 ):
        self.new_line = new_line
        self.timeout = timeout
        self.max_loop_retries = max_loop_retries
        self.empty_loop_timeout = empty_loop_timeout
        self.clear_buffer_timeout = clear_buffer_timeout
        # self.default_prompt = BasicPrompt
        self.prompt_factory = BasicPromptFactory
