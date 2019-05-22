import json
import os

import pkg_resources
import pytest

from mutagen_helper.parser import YamlProjectParser


@pytest.fixture
def parser():
    return YamlProjectParser()


def test_parser_with_and_without_sessions(parser: YamlProjectParser):
    with_sessions = parser.parse(pkg_resources.resource_filename(__name__, "data/test_parser_with_sessions.yml"))
    without_sessions = parser.parse(pkg_resources.resource_filename(__name__, "data/test_parser_without_sessions.yml"))
    assert 'sessions' in with_sessions
    assert 'sessions' in without_sessions
    assert with_sessions['sessions'] == without_sessions['sessions']


def test_parser_expandvars(parser: YamlProjectParser):
    os.environ['ALPHA'] = 'alpha'
    os.environ['BETA'] = 'beta'

    expandvars = parser.parse(pkg_resources.resource_filename(__name__, "data/test_parser_expandvars.yml"))
    expandvars_expected = parser.parse(pkg_resources.resource_filename(__name__, "data/test_parser_expandvars_expected.yml"))

    assert expandvars == expandvars_expected
