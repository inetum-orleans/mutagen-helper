import json
import os

import pkg_resources
import pytest

from mutagen_helper.parser import ProjectParser


@pytest.fixture
def parser():
    return ProjectParser()


def _remove_path_related_keys(data, key=None):
    if isinstance(data, list):
        for i, v in enumerate(data):
            data[i] = _remove_path_related_keys(v)
    elif isinstance(data, dict):
        for (k, v) in data.items():
            data[k] = _remove_path_related_keys(v, k)
    if key and key in ('configuration',):
        return '@TEST@'
    return data


def test_parser_with_and_without_sessions(parser: ProjectParser):
    with_sessions = next(parser.parse(pkg_resources.resource_filename(__name__, "data/test_parser_with_sessions.yml")))
    without_sessions = next(
        parser.parse(pkg_resources.resource_filename(__name__, "data/test_parser_without_sessions.yml")))

    assert _remove_path_related_keys(with_sessions['sessions']) == _remove_path_related_keys(
        without_sessions['sessions'])


def test_parser_expandvars(parser: ProjectParser):
    os.environ['ALPHA'] = 'alpha'
    os.environ['BETA'] = 'beta'

    expandvars = next(parser.parse(pkg_resources.resource_filename(__name__, "data/test_parser_expandvars.yml")))
    expandvars_expected = next(parser.parse(
        pkg_resources.resource_filename(__name__, "data/test_parser_expandvars_expected.yml")))

    assert _remove_path_related_keys(expandvars) == _remove_path_related_keys(expandvars_expected)


def test_parser_projects(parser: ProjectParser):
    projects = list(parser.parse(
        pkg_resources.resource_filename(__name__, "data/test_parser_projects.yml")))

    projects_expected = _remove_path_related_keys(
        json.load(pkg_resources.resource_stream(__name__, "data/test_parser_projects_expected.json")))

    assert _remove_path_related_keys(projects) == projects_expected
