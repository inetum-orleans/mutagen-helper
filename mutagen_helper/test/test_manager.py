import os

import pkg_resources
import pytest

from mutagen_helper.manager import Manager


@pytest.fixture
def manager(cwd_path):
    return Manager(True, db_filepath=os.path.join(cwd_path, 'db.json'))


@pytest.fixture
def cwd_path(tmp_path, request):
    cwd = os.getcwd()
    os.chdir(tmp_path)

    def restore_cwd():
        os.chdir(cwd)

    request.addfinalizer(restore_cwd)
    return tmp_path


def test_manager_project_files(manager: Manager, cwd_path):
    path1 = os.path.join(cwd_path, 'test1')
    path2 = os.path.join(cwd_path, 'test2')
    path3 = os.path.join(cwd_path, 'test3')
    path4 = os.path.join(path3, 'test4')

    os.mkdir(path1)
    os.mkdir(path2)
    os.mkdir(path3)
    os.mkdir(path4)

    files = list(manager.project_files(cwd_path))
    assert files == []

    mutagen1 = os.path.join(path1, '.mutagen.yml')
    mutagen2 = os.path.join(path3, '.mutagen.yaml')

    with open(os.path.join(path1, '.mutagen.yml'), 'w'):
        pass

    with open(os.path.join(path3, '.mutagen.yaml'), 'w'):
        pass

    with open(os.path.join(path4, '.mutagen.yaml'), 'w'):
        pass

    files = list(manager.project_files(cwd_path))
    assert mutagen1 in files and mutagen2 in files and len(files) == 2

    files = list(manager.project_files(mutagen1))
    assert files == [mutagen1]


def test_up_and_down(manager: Manager, cwd_path: str):
    path1 = os.path.join(cwd_path, 'test1')
    path2 = os.path.join(cwd_path, 'test2')
    path3 = os.path.join(cwd_path, 'test3')
    path4 = os.path.join(path3, 'test4')

    os.chdir(cwd_path)

    os.mkdir(path1)
    os.mkdir(path2)
    os.mkdir(path3)
    os.mkdir(path4)

    mutagen1 = os.path.join(path1, 'mutagen.yml')
    mutagen2 = os.path.join(path3, '.mutagen.yaml')

    with open(mutagen1, 'wb') as f:
        f.write(pkg_resources.resource_string(__name__, "data/test1.yml"))

    with open(mutagen2, 'wb') as f:
        f.write(pkg_resources.resource_string(__name__, "data/test3.yml"))

    manager._internals.wrapper.terminate()

    handled_sessions = manager.up(cwd_path)
    assert len(handled_sessions) == 2

    manager.flush(cwd_path)

    lst = manager.list(cwd_path)
    assert len(lst) == 2

    manager.down(cwd_path)

    lst = manager.list(cwd_path)
    assert len(lst) == 0


def test_up_twice_and_down_twice(manager: Manager, cwd_path: str):
    path1 = os.path.join(cwd_path, 'test1')
    path2 = os.path.join(cwd_path, 'test2')
    path3 = os.path.join(cwd_path, 'test3')
    path4 = os.path.join(path3, 'test4')

    os.chdir(cwd_path)

    os.mkdir(path1)
    os.mkdir(path2)
    os.mkdir(path3)
    os.mkdir(path4)

    mutagen1 = os.path.join(path1, '.mutagen.yml')
    mutagen2 = os.path.join(path3, '.mutagen.yaml')

    with open(mutagen1, 'wb') as f:
        f.write(pkg_resources.resource_string(__name__, "data/test1.yml"))

    with open(mutagen2, 'wb') as f:
        f.write(pkg_resources.resource_string(__name__, "data/test3.yml"))

    manager._internals.wrapper.terminate()

    handled_sessions = manager.up(cwd_path)
    assert len(handled_sessions) == 2

    handled_sessions = manager.up(cwd_path)
    assert len(handled_sessions) == 0

    lst = manager.list(cwd_path)
    assert len(lst) == 2

    handled_sessions = manager.down(cwd_path)
    assert len(handled_sessions) == 2

    handled_sessions = manager.down(cwd_path)
    assert len(handled_sessions) == 0

    lst = manager.list(cwd_path)
    assert len(lst) == 0


def test_up_and_down_with_resume_pause_flush(manager: Manager, cwd_path: str):
    path1 = os.path.join(cwd_path, 'test1')
    path2 = os.path.join(cwd_path, 'test2')
    path3 = os.path.join(cwd_path, 'test3')
    path4 = os.path.join(path3, 'test4')

    os.chdir(cwd_path)

    os.mkdir(path1)
    os.mkdir(path2)
    os.mkdir(path3)
    os.mkdir(path4)

    mutagen1 = os.path.join(path1, '.mutagen.yml')
    mutagen2 = os.path.join(path3, 'mutagen.yaml')

    with open(mutagen1, 'wb') as f:
        f.write(pkg_resources.resource_string(__name__, "data/test1.yml"))

    with open(mutagen2, 'wb') as f:
        f.write(pkg_resources.resource_string(__name__, "data/test3.yml"))

    manager._internals.wrapper.terminate()

    handled_sessions = manager.up(cwd_path)
    assert len(handled_sessions) == 2

    manager.flush(cwd_path)

    lst = manager.list(cwd_path)
    assert len(lst) == 2

    manager.pause(cwd_path)
    manager.resume(cwd_path)

    manager.down(cwd_path)

    lst = manager.list(cwd_path)
    assert len(lst) == 0
