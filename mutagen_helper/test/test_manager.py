import os

import pkg_resources
import pytest

from mutagen_helper.manager import Manager


@pytest.fixture
def manager(cwd_path):
    return Manager()


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


def test_up_and_down_with_project_and_session_name(manager: Manager, cwd_path: str):
    path1 = os.path.join(cwd_path, 'test1')
    path2 = os.path.join(cwd_path, 'test2')
    path3 = os.path.join(cwd_path, 'test3')
    path4 = os.path.join(path3, 'test4')

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

    handled_sessions = manager.down(project='test1')
    assert len(handled_sessions) == 1

    lst = manager.list(cwd_path)
    assert len(lst) == 1

    handled_sessions = manager.down(project='test3', session='blabla')
    assert len(handled_sessions) == 0

    handled_sessions = manager.down(project='test3', session='0')
    assert len(handled_sessions) == 1

    lst = manager.list(cwd_path)
    assert len(lst) == 0


def test_up_twice_and_down_twice(manager: Manager, cwd_path: str):
    path1 = os.path.join(cwd_path, 'test1')
    path2 = os.path.join(cwd_path, 'test2')
    path3 = os.path.join(cwd_path, 'test3')
    path4 = os.path.join(path3, 'test4')

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

    lst = manager.list(cwd_path)
    assert len(lst) == 2

    manager.down(cwd_path)

    lst = manager.list(cwd_path)
    assert len(lst) == 0


def test_auto_configure(manager: Manager, cwd_path: str):
    path1 = os.path.join(cwd_path, 'test1')
    path2 = os.path.join(cwd_path, 'test2')
    path3 = os.path.join(cwd_path, 'test3')
    path4 = os.path.join(cwd_path, 'test4')
    path5 = os.path.join(cwd_path, 'test5')

    os.mkdir(path1)
    os.mkdir(path2)
    os.mkdir(path3)
    os.mkdir(path4)
    os.mkdir(path5)

    mutagen1 = os.path.join(path1, '.mutagen.yml')
    mutagen3 = os.path.join(path3, 'mutagen.yaml')
    mutagen5 = os.path.join(path5, 'mutagen.yaml')
    mutagen_auto = os.path.join(cwd_path, 'mutagen.yaml')

    with open(mutagen1, 'wb') as f:
        f.write(pkg_resources.resource_string(__name__, "data/test1.yml"))

    with open(mutagen3, 'wb') as f:
        f.write(pkg_resources.resource_string(__name__, "data/test3.yml"))

    with open(mutagen5, 'wb') as f:
        f.write(pkg_resources.resource_string(__name__, "data/test5.yml"))

    with open(mutagen_auto, 'wb') as f:
        f.write(pkg_resources.resource_string(__name__, "data/test_auto.yml"))

    manager._internals.wrapper.terminate()

    handled_sessions = manager.up(cwd_path)
    assert len(handled_sessions) == 5

    lst = manager.list(cwd_path)
    assert len(lst) == 5
    project_names = list(map(lambda item: item['Mutagen Helper']['Project name'], lst))
    betas = list(map(lambda item: item['Beta']['URL'], lst))

    assert len(project_names) == 5
    assert set(project_names) == {'test1', 'test2', 'test3', 'test4', 'test5'}

    assert any(beta.endswith(os.path.join('beta1', 'test1')) for beta in betas)
    assert any(beta.endswith(os.path.join('beta_auto', 'test2')) for beta in betas)
    assert any(beta.endswith(os.path.join('beta3')) for beta in betas)
    assert any(beta.endswith(os.path.join('beta_auto', 'test4')) for beta in betas)
    assert any(beta.endswith(os.path.join('beta5', 'test5')) for beta in betas)

    manager.down(cwd_path)

    lst = manager.list(cwd_path)
    assert len(lst) == 0


def test_auto_configure_ignore_project_configuration(manager: Manager, cwd_path: str):
    path1 = os.path.join(cwd_path, 'test1')
    path2 = os.path.join(cwd_path, 'test2')
    path3 = os.path.join(cwd_path, 'test3')
    path4 = os.path.join(cwd_path, 'test4')
    path5 = os.path.join(cwd_path, 'test5')

    os.mkdir(path1)
    os.mkdir(path2)
    os.mkdir(path3)
    os.mkdir(path4)
    os.mkdir(path5)

    mutagen1 = os.path.join(path1, '.mutagen.yml')
    mutagen3 = os.path.join(path3, 'mutagen.yaml')
    mutagen5 = os.path.join(path5, 'mutagen.yaml')
    mutagen_auto = os.path.join(cwd_path, 'mutagen.yaml')

    with open(mutagen1, 'wb') as f:
        f.write(pkg_resources.resource_string(__name__, "data/test1.yml"))

    with open(mutagen3, 'wb') as f:
        f.write(pkg_resources.resource_string(__name__, "data/test3.yml"))

    with open(mutagen5, 'wb') as f:
        f.write(pkg_resources.resource_string(__name__, "data/test5.yml"))

    with open(mutagen_auto, 'wb') as f:
        f.write(pkg_resources.resource_string(__name__, "data/test_auto_ignore_project_configuration.yml"))

    manager._internals.wrapper.terminate()

    handled_sessions = manager.up(cwd_path)
    assert len(handled_sessions) == 5

    lst = manager.list(cwd_path)
    assert len(lst) == 5
    project_names = list(map(lambda item: item['Mutagen Helper']['Project name'], lst))
    betas = list(map(lambda item: item['Beta']['URL'], lst))

    assert len(project_names) == 5
    assert set(project_names) == {'test1', 'test2', 'test3', 'test4', 'test5'}

    assert any(beta.endswith(os.path.join('beta_auto', 'test1')) for beta in betas)
    assert any(beta.endswith(os.path.join('beta_auto', 'test2')) for beta in betas)
    assert any(beta.endswith(os.path.join('beta_auto', 'test3')) for beta in betas)
    assert any(beta.endswith(os.path.join('beta_auto', 'test4')) for beta in betas)
    assert any(beta.endswith(os.path.join('beta_auto', 'test5')) for beta in betas)

    manager.down(cwd_path)

    lst = manager.list(cwd_path)
    assert len(lst) == 0


def test_auto_configure_advanced(manager: Manager, cwd_path: str):
    path1 = os.path.join(cwd_path, 'test1')
    path2 = os.path.join(cwd_path, 'test2')
    path3 = os.path.join(cwd_path, 'test3')
    path4 = os.path.join(cwd_path, 'test4')
    path5 = os.path.join(cwd_path, 'test5')

    os.mkdir(path1)
    os.mkdir(path2)
    os.mkdir(path3)
    os.mkdir(path4)
    os.mkdir(path5)

    mutagen1 = os.path.join(path1, '.mutagen.yml')
    mutagen3 = os.path.join(path3, 'mutagen.yaml')
    mutagen5 = os.path.join(path5, 'mutagen.yaml')
    mutagen_auto = os.path.join(cwd_path, 'mutagen.yaml')

    with open(mutagen1, 'wb') as f:
        f.write(pkg_resources.resource_string(__name__, "data/test1.yml"))

    with open(mutagen3, 'wb') as f:
        f.write(pkg_resources.resource_string(__name__, "data/test3.yml"))

    with open(mutagen5, 'wb') as f:
        f.write(pkg_resources.resource_string(__name__, "data/test5.yml"))

    with open(mutagen_auto, 'wb') as f:
        f.write(pkg_resources.resource_string(__name__, "data/test_auto_advanced.yml"))

    manager._internals.wrapper.terminate()

    handled_sessions = manager.up(cwd_path)
    assert len(handled_sessions) == 3

    lst = manager.list(cwd_path)
    assert len(lst) == 3
    project_names = list(map(lambda item: item['Mutagen Helper']['Project name'], lst))
    betas = list(map(lambda item: item['Beta']['URL'], lst))

    assert len(project_names) == 3
    assert set(project_names) == {'test2', 'test5', 'test3'}

    assert any(beta.endswith(os.path.join('beta_auto', 'test2')) for beta in betas)
    assert any(beta.endswith(os.path.join('beta3')) for beta in betas)
    assert any(beta.endswith(os.path.join('beta_auto', 'test5')) for beta in betas)

    manager.pause(cwd_path)
    manager.resume(cwd_path)

    manager.down(cwd_path)

    lst = manager.list(cwd_path)
    assert len(lst) == 0
