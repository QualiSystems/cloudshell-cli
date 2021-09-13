from cloudshell.cli.session.prompt.factory import BasicPromptFactory


class Config:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


class SessionConfig(Config):
    new_line: str = "\r"
    timeout: int = 30
    max_loop_retries: int = 20
    empty_loop_timeout: float = 0.5
    clear_buffer_timeout: float = 0.1
    # use_exact_prompt: bool = True
    prompt_factory: BasicPromptFactory = BasicPromptFactory()
    prompt_timeout: int = 2
    active_timeout: int = 60
    reconnect_timeout: int = 30
