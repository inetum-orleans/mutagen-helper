import json
import os

import pkg_resources
import pytest

from mutagen_helper.wrapper import MutagenWrapper


@pytest.fixture
def wrapper():
    return MutagenWrapper()


@pytest.fixture
def cwd_path(tmp_path, request):
    cwd = os.getcwd()
    os.chdir(tmp_path)

    def restore_cwd():
        os.chdir(cwd)

    request.addfinalizer(restore_cwd)
    return tmp_path


def test_create_and_terminate(wrapper: MutagenWrapper, cwd_path):
    alpha = os.path.join(cwd_path, 'alpha')
    beta = os.path.join(cwd_path, 'beta')

    session_id = wrapper.create(alpha, beta)
    try:
        assert len(session_id)
        assert session_id.count('-') == 4
    finally:
        wrapper.terminate(session_id)


def test_list(wrapper: MutagenWrapper, cwd_path):
    wrapper.terminate()

    alpha1 = os.path.join(cwd_path, 'alpha1')
    beta1 = os.path.join(cwd_path, 'beta1')

    alpha2 = os.path.join(cwd_path, 'alpha2')
    beta2 = os.path.join(cwd_path, 'beta2')

    try:
        wrapper.create(alpha1, beta1)
        wrapper.create(alpha2, beta2)

        wrapper.flush()

        lst = wrapper.list()
        assert len(lst) == 2
    finally:
        wrapper.terminate()


def test_parse(wrapper: MutagenWrapper):
    data = wrapper.list_parser.parse(
        str(pkg_resources.resource_string(__name__, "data/mutagen.log"), encoding='UTF-8'))
    expected_data = json.load(pkg_resources.resource_stream(__name__, "data/mutagen.json"), encoding='UTF-8')
    assert data == expected_data


def test_parse_with_problems(wrapper: MutagenWrapper):
    data = wrapper.list_parser.parse(
        str(pkg_resources.resource_string(__name__, "data/mutagen-problems.log"), encoding='UTF-8'))
    expected_data = json.load(pkg_resources.resource_stream(__name__, "data/mutagen-problems.json"), encoding='UTF-8')
    assert data == expected_data


def test_parse_with_ignores(wrapper: MutagenWrapper):
    data = wrapper.list_parser.parse(
        str(pkg_resources.resource_string(__name__, "data/mutagen.log"), encoding='UTF-8'))
    expected_data = json.load(pkg_resources.resource_stream(__name__, "data/mutagen.json"), encoding='UTF-8')
    assert data == expected_data
