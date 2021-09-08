from cloudshell.cli.session.core.config import Config, DefaultValue


class ProcessingConfig(Config):
    loop_detector_max_action_loops: int = DefaultValue(3)
    loop_detector_max_combination_length: int = DefaultValue(4)
    reconnect_timeout: int = DefaultValue(30)
    remove_command: bool = DefaultValue(True)
    use_exact_prompt: bool = DefaultValue(True)
