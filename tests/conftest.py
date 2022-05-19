import logging

import pytest


@pytest.fixture()
def logger():
    return logging.getLogger(__file__)
