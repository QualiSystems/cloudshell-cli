import re
from abc import ABCMeta, abstractmethod

ABC = ABCMeta("ABC", (object,), {"__slots__": ()})


class AbstractPrompt(ABC):
    """Prompt model.

    Encapsulate mechanism for matching session prompt.
    """

    @abstractmethod
    def match(self, data):
        """Main verification for the prompt match.

        :param str data: Match string
        :rtype: bool
        """
        pass


class BasicPrompt(AbstractPrompt):
    def __init__(self, prompt_pattern, source_data=None):
        self.prom_pattern = prompt_pattern
        self.source_data = source_data
        self._compiled_pattern = re.compile(re.escape(prompt_pattern), re.DOTALL)

    def __eq__(self, other: AbstractPrompt):
        if self.source_data:
            return other.match(self.source_data)
        return self.match(str(other)) or other.match(str(self))

    def __str__(self):
        return self.prom_pattern

    def __repr__(self):
        return self.__str__()

    def match(self, data):
        return bool(self._compiled_pattern.search(data))
