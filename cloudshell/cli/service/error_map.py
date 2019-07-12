from collections import OrderedDict
import re

from cloudshell.cli.session.session_exceptions import CommandExecutionException


class Error:
    def __init__(self, pattern, error):
        """

        :param str pattern:
        :param str|CommandExecutionException error:
        """
        self.pattern = pattern
        self.compiled_pattern = re.compile(pattern=pattern, flags=re.DOTALL)
        self.error = error

    def __call__(self, output):
        """

        :param str output:
        :raises: CommandExecutionException
        """
        if isinstance(self.error, CommandExecutionException):
            raise self.error

        raise CommandExecutionException(f"Session returned '{self.error}'")

    def __repr__(self):
        """

        :rtype: str
        """
        return f"{super().__repr__()} pattern: {self.pattern}, error: {self.error}"

    def match(self, output):
        """

        :param str output:
        :rtype: bool
        """
        return bool(self.compiled_pattern.search(output))


class ErrorMap:
    def __init__(self, errors=None):
        """

        :param list[Error] errors:
        """
        if errors is None:
            errors = []

        self._errors_dict = OrderedDict([(error.pattern, error) for error in errors])

    @property
    def errors(self):
        """

        :rtype: list[Error]
        """
        return list(self._errors_dict.values())

    def add(self, error):
        """

        :param Error error:
        :return:
        """
        self._errors_dict[error.pattern] = error

    def extend(self, error_map, override=False):
        """

        :param ErrorMap error_map:
        :param bool override:
        :return:
        """
        for error in error_map.errors:
            if not override and error.pattern in self._errors_dict:
                continue
            self.add(error)

    def process(self, output, logger):
        """

        :param str output:
        :param logging.Logger logger:
        :rtype: bool
        """

        for error in self.errors:
            if error.match(output):
                logger.debug(f"Matched Error with pattern: {error.pattern}")
                error(output)

    def __add__(self, other):
        """

        :param other:
        :rtype: ActionMap
        """
        error_map_class = type(self)
        if isinstance(other, error_map_class):
            error_map = error_map_class(errors=self.errors)
            error_map.extend(other)
            return error_map

        raise TypeError(f"unsupported operand type(s) for +: '{type(self)}' and '{type(other)}'")

    def __repr__(self):
        """

        :rtype: str
        """
        return f"{super().__repr__()} errors: {self.errors}"
