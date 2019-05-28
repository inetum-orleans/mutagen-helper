import fnmatch
import os

from mutagen_helper.parser import ProjectParser


def configuration_file(path):
    candidates = ['mutagen.yml', 'mutagen.yaml', '.mutagen.yml', '.mutagen.yaml']
    for candidate in candidates:
        candidate_path = os.path.join(path, candidate)
        if os.path.isfile(os.path.join(path, candidate)):
            return candidate_path
    return None


def configuration_files(path):
    if os.path.isdir(path):
        group_file = configuration_file(path)
        if group_file:
            yield group_file
        else:
            for item in os.listdir(path):
                child_path = os.path.join(path, item)
                if os.path.isdir(os.path.join(path, child_path)):
                    child_project_file = configuration_file(child_path)
                    if child_project_file:
                        yield child_project_file
    elif os.path.isfile(path):
        yield path


def _path_matches(item, include=None, exclude=None):
    if exclude:
        if isinstance(exclude, bool):
            return not exclude
        else:
            for exclude_item in exclude:
                if fnmatch.fnmatch(item, exclude_item):
                    return False
    if include:
        if isinstance(include, bool):
            return True
        else:
            for include_item in include:
                if fnmatch.fnmatch(item, include_item):
                    return True
            return False
    return True


def auto_configure(path, auto=True, parser: ProjectParser = None):
    if os.path.isfile(path):
        path = os.path.dirname(path)

    if isinstance(auto, bool):
        auto = {'enabled': auto, 'include': None, 'exclude': None, 'ignore_project_configuration': False}

    if auto.get('enabled', True):
        if auto.get('exclude') and not isinstance(auto.get('exclude'), list):
            auto['exclude'] = [auto.get('exclude')]

        if auto.get('include') and not isinstance(auto.get('include'), list):
            auto['include'] = [auto.get('include')]

        for item in os.listdir(path):
            child_path = os.path.join(path, item)
            if os.path.isdir(child_path):
                child_fullpath = os.path.join(path, child_path)
                child_project_file = configuration_file(child_fullpath)
                if child_project_file and parser and \
                        _path_matches(item, exclude=auto.get('ignore_project_configuration')):
                    for project in parser.parse(child_project_file):
                        yield project
                else:
                    if _path_matches(item, auto.get('include'), auto.get('exclude')):
                        yield {'path': child_fullpath, 'auto_configured': True}
