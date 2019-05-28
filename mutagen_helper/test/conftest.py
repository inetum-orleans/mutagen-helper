# content of conftest.py or a tests file (e.g. in your tests or root directory)
import os

import pytest


@pytest.fixture(scope="session", autouse=True)
def cleanup_environment_variables(request):
    for k, v in os.environ.items():
        if k.startswith('MUTAGEN_HELPER'):
            del os.environ[k]
