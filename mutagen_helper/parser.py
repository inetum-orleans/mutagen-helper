import os

import yaml


class ProjectParser:
    def handle_inheritance(self, data):
        if 'sessions' not in data:
            session = {}
            data['sessions'] = [session]
        for k, v in data.items():
            if k in ('sessions',):
                continue
            for session in data['sessions']:
                if k not in session:
                    session[k] = v

    def expandvars(self, data):
        if isinstance(data, dict):
            mapped = {}
            for k, v in data.items():
                mapped[k] = self.expandvars(v)
            return mapped
        elif isinstance(data, list):
            return list(map(self.expandvars, data))
        elif isinstance(data, str):
            return os.path.expandvars(data)
        return data

    def add_project_default_values(self, data, path=None):
        if path and not data.get('project_name'):
            data['project_name'] = os.path.basename(os.path.dirname(os.path.normpath(path)))

        data['alpha'] = data.get('alpha',
                                 os.environ.get('MUTAGEN_HELPER_ALPHA', os.path.dirname(path)))
        data['beta'] = data.get('beta', os.environ.get('MUTAGEN_HELPER_BETA'))
        data['append_project_name_to_beta'] = data.get('append_project_name_to_beta',
                                                       os.environ.get('MUTAGEN_HELPER_APPEND_PROJECT_NAME_TO_BETA',
                                                                      True))

    def add_sessions_default_values(self, data):
        for i, session in enumerate(data['sessions']):
            session['name'] = session.get('name', str(i))

    def parse_data(self, data: dict, path=None):
        self.add_project_default_values(data, path=path)
        self.handle_inheritance(data)
        self.add_sessions_default_values(data)
        data = self.expandvars(data)
        return data


class YamlProjectParser(ProjectParser):
    def parse(self, path: str):
        with open(path, 'r') as stream:
            data = yaml.safe_load(stream)
            return self.parse_data(data, path)
