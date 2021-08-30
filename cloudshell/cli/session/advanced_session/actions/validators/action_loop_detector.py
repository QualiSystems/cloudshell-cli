class ActionLoopDetector:
    """Help to detect loops for action combinations"""

    def __init__(self, max_loops, max_combination_length):
        """

        :param max_loops:
        :param max_combination_length:
        :return:
        """
        self._max_action_loops = max_loops
        self._max_combination_length = max_combination_length
        self._action_history = []

    def loops_detected(self, action_pattern):
        """Add action key to the history and detect loops

        :param str action_pattern:
        :return:
        """
        self._action_history.append(action_pattern)
        for combination_length in range(1, self._max_combination_length + 1):
            if self._is_combination_compatible(combination_length):
                if self._is_loop_exists(combination_length):
                    return True
        return False

    def _is_combination_compatible(self, combination_length):
        """Check if combinations may exist

        :param combination_length:
        :return:
        """
        return len(self._action_history) / combination_length >= self._max_action_loops

    def _is_loop_exists(self, combination_length):
        """Detect loops for combination length

        :param combination_length:
        :return:
        """
        reversed_history = self._action_history[::-1]
        combinations = [reversed_history[x:x + combination_length] for x in
                        range(0, len(reversed_history), combination_length)][:self._max_action_loops]
        for x, y in [combinations[x:x + 2] for x in range(0, len(combinations) - 1)]:
            if x != y:
                return False
        return True
