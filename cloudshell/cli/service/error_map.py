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
        self.error = error

    def __call__(self):
        """

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
        return bool(re.search(self.pattern, output, re.DOTALL))


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

    def __call__(self, output, logger):
        """

        :param str output:
        :param logging.Logger logger:
        :rtype: bool
        """

        for error in self.errors:
            if error.match(output):
                logger.debug(f"Matched Error with pattern: {error.pattern}")
                error()

    def __add__(self, other):
        """

        :param other:
        :rtype: ActionMap
        """
        if isinstance(other, type(self)):
            errors = self.errors + [error for error in other.errors if error.pattern not in
                                    [error.pattern for error in self.errors]]

            return ErrorMap(errors=errors)

        raise TypeError(f"unsupported operand type(s) for +: '{type(self)}' and '{type(other)}'")

    def __repr__(self):
        """

        :rtype: str
        """
        return f"{super().__repr__()} errors: {self.errors}"
