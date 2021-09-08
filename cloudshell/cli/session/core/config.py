from cloudshell.cli.session.prompt.factory import BasicPromptFactory


class Config:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


class DefaultValue(object):
    def __init__(self, value):
        self.value = value

    def __get__(self, instance: Config, owner):
        return self.value


class SessionConfig(Config):
    new_line: str = DefaultValue("\r")
    timeout: int = DefaultValue(30)
    max_loop_retries: int = DefaultValue(20)
    empty_loop_timeout: float = DefaultValue(0.5)
    clear_buffer_timeout: float = DefaultValue(0.1)
    prompt_factory = DefaultValue(BasicPromptFactory)
    active_timeout = DefaultValue(60)
