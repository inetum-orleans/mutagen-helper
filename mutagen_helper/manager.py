import copy
import logging
import os

from click import ClickException

from .parser import YamlProjectParser
from .wrapper import MutagenWrapper

db_filepath = os.path.join(
    os.environ.get("MUTAGEN_HELPER_HOME", os.path.join(os.path.expanduser("~"), ".mutagen-helper")), "db.json")


class ManagerException(ClickException):
    pass


class ManagerInternals:
    def __init__(self, purge=False, filepath=db_filepath):
        self.project_parser = YamlProjectParser()
        self.wrapper = MutagenWrapper()
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

    def _effective_beta(self, session, project_name):
        beta = session['beta']
        if session['append_project_name_to_beta'] \
                and not beta.endswith('/' + project_name) and not beta.endswith('\\' + project_name):
            if beta.endswith('/') or beta.endswith('\\'):
                beta = beta + project_name
            beta = beta + '/' + project_name
        return beta

    def _build_label_list(self, project_name, name=None, alpha=None, beta=None, selector=False):
        labels = []
        value_separator = "==" if selector else "="
        if project_name:
            labels.append("project_name%s%s" % (value_separator, project_name))
        if name:
            labels.append("name%s%s" % (value_separator, name))
        if alpha:
            labels.append("alpha%s%s" % (value_separator, alpha))
        if beta:
            labels.append("beta%s%s" % (value_separator, beta))
        return labels

    def _build_label_selector(self, project_name, name=None, alpha=None, beta=None):
        return ','.join(self._build_label_list(project_name, name, alpha, beta, selector=True))

    def _dispatch_project_files(self, path, dispatcher_function, dispatch_session=False):
        betas = dict()
        for session_info in self.wrapper.list():
            betas[os.path.abspath(os.path.normpath(session_info['Beta configuration']['URL']))] = session_info

        for project_file in self.project_files(path):
            project = self.project_parser.parse(project_file)
            project_name = project['project_name']
            for session in project['sessions']:
                betas[os.path.abspath(
                    os.path.normpath(self._effective_beta(session, project_name)))] = session

        ret = []
        for project_file in self.project_files(path):
            project = self.project_parser.parse(project_file)
            project_name = project['project_name']
            if dispatch_session:
                for session in project['sessions']:
                    beta_counterpart = betas.get(os.path.abspath(os.path.dirname(os.path.normpath((project_file)))))
                    if beta_counterpart:
                        logging.debug("Skip file %s because it match beta of session %s (%s)." % (
                            project_file, beta_counterpart['project_name'], beta_counterpart['name']))
                        continue
                    dispatcher_ret = dispatcher_function(session, project_name)
                    if dispatcher_ret is not None:
                        ret.append(dispatcher_ret)
            else:
                dispatcher_ret = dispatcher_function(project_name)
                if dispatcher_ret:
                    ret.extend(dispatcher_ret)

        return ret

    def up(self, path):
        return self._dispatch_project_files(path, self.up_session, dispatch_session=True)

    def up_session(self, session, project_name):
        name = session['name']

        session_info = self.wrapper.list(label_selector=self._build_label_selector(project_name, session['name']),
                                         one=True)
        if session_info:
            logging.info('Session %s[%s] (%s) already exists.' % (project_name, name, session_info['Session']))
            return
        else:
            logging.debug('No session %s[%s] found.' % (name, project_name))

        alpha = session['alpha']
        beta = self._effective_beta(session, project_name)
        options = copy.deepcopy(session.get('options', {}))
        if 'label' not in options:
            options['label'] = self._build_label_list(project_name, session['name'])
        else:
            options['label'].extend(self._build_label_list(project_name, session['name']))

        session_id = self.wrapper.create(alpha, beta, options)
        logging.info('Session %s[%s] (%s) created.' % (project_name, name, session_id))

        return session_id

    def down(self, path):
        return self._dispatch_project_files(path, self.down_project)

    def down_project(self, project_name):
        session_ids = self.wrapper.terminate(label_selector=self._build_label_selector(project_name))
        for session_id in session_ids:
            logging.info('Session %s (%s) terminated.' % (project_name, session_id))
        return session_ids

    def flush(self, path):
        return self._dispatch_project_files(path, self.flush_project)

    def flush_project(self, project_name):
        session_ids = self.wrapper.flush(label_selector=self._build_label_selector(project_name))
        for session_id in session_ids:
            logging.info('Session %s (%s) flushed.' % (project_name, session_id))
        return session_ids

    def pause(self, path):
        return self._dispatch_project_files(path, self.pause_project)

    def pause_project(self, project_name):
        session_ids = self.wrapper.pause(label_selector=self._build_label_selector(project_name))
        for session_id in session_ids:
            logging.info('Session %s (%s) paused.' % (project_name, session_id))
        return session_ids

    def resume(self, path):
        return self._dispatch_project_files(path, self.resume_project)

    def resume_project(self, project_name):
        session_id = self.wrapper.resume(label_selector=self._build_label_selector(project_name))
        logging.info('Session %s (%s) resumed.' % (project_name, session_id))
        return session_id

    def project_file(self, path):
        candidates = ['mutagen.yml', 'mutagen.yaml', '.mutagen.yml', '.mutagen.yaml']
        for candidate in candidates:
            candidate_path = os.path.join(path, candidate)
            if os.path.isfile(os.path.join(path, candidate)):
                return candidate_path
        return

    def list(self, path):
        return self._dispatch_project_files(path, self.list_session, dispatch_session=True)

    def list_session(self, session, project_name):
        mutagen_session = self.wrapper.list(label_selector=self._build_label_selector(project_name, session['name']),
                                            one=True)
        if mutagen_session:
            mutagen_session['Project name'] = project_name
            mutagen_session['Name'] = session['name']

        return mutagen_session

    def project_files(self, path):
        if os.path.isdir(path):
            group_file = self.project_file(path)
            if group_file:
                yield group_file
            else:
                for item in os.listdir(path):
                    child_path = os.path.join(path, item)
                    if os.path.isdir(os.path.join(path, child_path)):
                        child_project_file = self.project_file(child_path)
                        if child_project_file:
                            yield child_project_file
        elif os.path.isfile(path):
            yield path
        else:
            raise


class Manager:
    def __init__(self, purge=False, db_filepath=db_filepath):
        self._internals = ManagerInternals(purge, db_filepath)

    def _sanitize_path(self, path):
        if path:
            return path
        else:
            return os.getcwd()

    def up(self, path):
        return self._internals.up(self._sanitize_path(path))

    def down(self, path):
        return self._internals.down(self._sanitize_path(path))

    def resume(self, path):
        return self._internals.resume(self._sanitize_path(path))

    def pause(self, path):
        return self._internals.pause(self._sanitize_path(path))

    def list(self, path):
        return self._internals.list(self._sanitize_path(path))

    def flush(self, path):
        return self._internals.flush(self._sanitize_path(path))

    def project_files(self, path):
        return self._internals.project_files(self._sanitize_path(path))

    def project_file(self, path):
        return self._internals.project_file(self._sanitize_path(path))
