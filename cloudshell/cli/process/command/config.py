from cloudshell.cli.session.core.config import SessionConfig


class ProcessingConfig(SessionConfig):
    loop_detector_max_action_loops: int = 3
    loop_detector_max_combination_length: int = 4
    remove_command: bool = True
    use_exact_prompt: bool = True
