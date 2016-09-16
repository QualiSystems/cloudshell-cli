from cloudshell.cli.node import Node, NodeOperations


class Prompt(Node):
    """
    Class describes our prompt and implement enter and exit command functions
    """
    DEFINED_PROMPTS = []

    def __init__(self, prompt, enter_command, exit_command, default_action=None, expected_map=None, error_map=None):
        """
        :param prompt:
        :param enter_command:
        :param exit_command:
        :param default_action:
        :param expected_map:
        :param error_map:
        :return:
        """
        super(Prompt, self).__init__()
        self._prompt = prompt
        self._enter_command = enter_command
        self._exit_command = exit_command
        self._default_actions = default_action
        self._expected_map = expected_map
        self._error_map = error_map

    def connect_prompt(self, prompt):
        """
        Connect child prompt
        :param prompt:
        :return:
        """
        self.add_child_node(prompt)
        Prompt.DEFINED_PROMPTS.append(prompt)

    def step_down(self):
        """
        Called when do exit
        :return:
        """
        print(self._exit_command + ' ' + str(self._prompt))

    def step_up(self):
        """
        Called when do enter
        :return:
        """
        print(self._enter_command + ' ' + str(self._prompt))


if __name__ == '__main__':
    pp1 = Prompt(1, 'enter', 'exit')
    pp2 = Prompt(2, 'enter', 'exit')
    pp3 = Prompt(3, 'enter', 'exit')
    pp4 = Prompt(4, 'enter', 'exit')
    pp5 = Prompt(5, 'enter', 'exit')
    pp6 = Prompt(6, 'enter', 'exit')

    pp1.connect_prompt(pp2)
    pp2.connect_prompt(pp3)
    pp3.connect_prompt(pp4)
    pp4.connect_prompt(pp5)
    pp3.connect_prompt(pp6)
    steps = NodeOperations.calculate_route_steps(pp6, pp5)
    map(lambda x: x(), steps)
