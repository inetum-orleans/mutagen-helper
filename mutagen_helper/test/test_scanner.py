import os

import pytest

from mutagen_helper import scanner
from mutagen_helper.parser import ProjectParser
from mutagen_helper.scanner import AutoConfigureNoProject


@pytest.fixture
def cwd_path(tmp_path, request):
    cwd = os.getcwd()
    os.chdir(tmp_path)

    def restore_cwd():
        os.chdir(cwd)

    request.addfinalizer(restore_cwd)
    return tmp_path


@pytest.fixture
def parser():
    return ProjectParser()


def test_auto_default(cwd_path: str, parser: ProjectParser):
    path1 = os.path.join(cwd_path, 'test1')
    path2 = os.path.join(cwd_path, 'test2')
    path3 = os.path.join(cwd_path, 'test3')
    path4 = os.path.join(path3, 'test4')

    os.mkdir(path1)
    os.mkdir(path2)
    os.mkdir(path3)
    os.mkdir(path4)

    config = list(scanner.auto_configure(cwd_path, parser=parser))

    assert len(config) == 3
    assert 'auto_configured' in config[0]
    assert config[0]['auto_configured']
    assert 'auto_configured' in config[1]
    assert config[1]['auto_configured']
    assert 'auto_configured' in config[2]
    assert config[2]['auto_configured']


def test_auto_includes(cwd_path: str):
    path1 = os.path.join(cwd_path, 'include1')
    path2 = os.path.join(cwd_path, 'include2')
    path3 = os.path.join(cwd_path, 'test3')
    path4 = os.path.join(path3, 'include4')

    os.mkdir(path1)
    os.mkdir(path2)
    os.mkdir(path3)
    os.mkdir(path4)

    config = list(scanner.auto_configure(cwd_path, {'enabled': True, 'include': ['include*']}, parser=parser))

    assert len(config) == 2
    assert 'auto_configured' in config[0]
    assert config[0]['auto_configured']
    assert 'auto_configured' in config[1]
    assert config[1]['auto_configured']


def test_auto_excludes(cwd_path: str):
    path1 = os.path.join(cwd_path, 'test1')
    path2 = os.path.join(cwd_path, 'exclude2')
    path3 = os.path.join(cwd_path, 'exclude3')
    path4 = os.path.join(path3, 'test4')

    os.mkdir(path1)
    os.mkdir(path2)
    os.mkdir(path3)
    os.mkdir(path4)

    config = list(scanner.auto_configure(cwd_path, {'enabled': True, 'exclude': ['exclude*']}, parser=parser))

    assert len(config) == 1
    assert 'auto_configured' in config[0]
    assert config[0]['auto_configured']


def test_auto_no_project(cwd_path: str):
    with pytest.raises(AutoConfigureNoProject):
        list(scanner.auto_configure(cwd_path, {'enabled': True, 'exclude': ['*']}, parser=parser))
