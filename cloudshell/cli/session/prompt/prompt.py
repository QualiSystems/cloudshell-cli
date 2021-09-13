import re


class Prompt(object):
    def __init__(self, pattern, source_data=None):
        self.pattern = pattern
        self.source_data = source_data
        self._compiled_pattern = re.compile(self.pattern, re.DOTALL)

    def __eq__(self, other: "Prompt"):
        if self.source_data:
            return other.match(self.source_data)
        return self.match(str(other)) or other.match(str(self))

    def __str__(self):
        return self.pattern

    def __repr__(self):
        return self.__str__()

    def match(self, data):
        return bool(self._compiled_pattern.search(data))
