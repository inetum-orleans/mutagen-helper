import os

import yaml
from expandvars import expandvars

from mutagen_helper import scanner


class ProjectParser:
    def handle_project_inheritance(self, project):
        if 'sessions' not in project:
            session = {}
            project['sessions'] = [session]
        for k, v in project.items():
            if k in ('sessions', 'auto_configure'):
                continue
            for session in project['sessions']:
                if k not in session:
                    session[k] = v

    def handle_data_inheritance(self, data):
        for k, v in data.items():
            if k in ('projects', 'auto_configure'):
                continue
            for project in data['projects']:
                if k not in project:
                    project[k] = v

    def expandvars(self, data):
        if isinstance(data, dict):
            mapped = {}
            for k, v in data.items():
                mapped[k] = self.expandvars(v)
            return mapped
        elif isinstance(data, list):
            return list(map(self.expandvars, data))
        elif isinstance(data, str):
            return expandvars(data.replace('\\', '\\\\'))
        return data

    def add_project_default_values(self, data, path=None):
        if path and not data.get('path'):
            data['path'] = os.path.dirname(os.path.normpath(path))

        if not data.get('project_name') and data.get('path'):
            data['project_name'] = os.path.basename(data['path'])

        data['alpha'] = data.get('alpha',
                                 os.environ.get('MUTAGEN_HELPER_ALPHA', data.get('path')))
        data['beta'] = data.get('beta', os.environ.get('MUTAGEN_HELPER_BETA'))
        data['append_project_name_to_beta'] = data.get('append_project_name_to_beta',
                                                       os.environ.get('MUTAGEN_HELPER_APPEND_PROJECT_NAME_TO_BETA',
                                                                      True))

    def add_project_sessions_default_values(self, data):
        for i, session in enumerate(data['sessions']):
            session['name'] = session.get('name', str(i))

    def parse_project(self, project: dict, path=None):
        self.add_project_default_values(project, path=path)
        self.handle_project_inheritance(project)
        self.add_project_sessions_default_values(project)
        project = self.expandvars(project)
        return project

    def parse_data(self, data: dict, path=None):
        if data.get('auto_configure'):
            auto_configured_projects = list(scanner.auto_configure(path, data.get('auto_configure'), self))
            if auto_configured_projects:
                if 'projects' not in data:
                    data['projects'] = []
                else:
                    tmp_auto_configure = data.pop('auto_configure')
                    data['projects'] = [data]
                    data['auto_configure'] = tmp_auto_configure
                data['projects'].extend(auto_configured_projects)

        if 'projects' in data:
            data['configuration'] = path
            self.handle_data_inheritance(data)
            for project in data['projects']:
                yield self.parse_project(project, path)
        else:
            data['configuration'] = path
            yield self.parse_project(data, path)

    def parse(self, configuration_filepath: str):
        with open(configuration_filepath, 'r') as stream:
            data = yaml.safe_load(stream)
        return self.parse_data(data, configuration_filepath)
