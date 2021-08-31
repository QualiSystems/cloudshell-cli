class ProcessingConfig(object):
    LOOP_DETECTOR_MAX_ACTION_LOOPS = 3
    LOOP_DETECTOR_MAX_COMBINATION_LENGTH = 4
    RECONNECT_TIMEOUT = 30
    REMOVE_COMMAND = True
    USE_EXACT_PROMPT = True

    def __init__(self,
                 loop_detector=True,
                 loop_detector_max_action_loops=LOOP_DETECTOR_MAX_ACTION_LOOPS,
                 loop_detector_max_combination_length=LOOP_DETECTOR_MAX_COMBINATION_LENGTH,
                 reconnect_timeout=RECONNECT_TIMEOUT,
                 remove_command=REMOVE_COMMAND,
                 use_exact_prompt=USE_EXACT_PROMPT
                 ):
        self.loop_detector = loop_detector
        self.loop_detector_max_action_loops = loop_detector_max_action_loops
        self.loop_detector_max_combination_length = (
            loop_detector_max_combination_length
        )

        self.reconnect_timeout = reconnect_timeout
        self.remove_command = remove_command
        self.use_exact_prompt = use_exact_prompt
