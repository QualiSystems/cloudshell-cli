import logging
import sys

import pytest


@pytest.fixture()
def logger():
    return logging.getLogger(__file__)


def pytest_ignore_collect(path):
    if sys.version_info.major == 2:
        if str(path).endswith("_py3.py"):
            return True
