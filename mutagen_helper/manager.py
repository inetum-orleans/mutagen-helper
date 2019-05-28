import copy
import logging
import os

from mutagen_helper import scanner
from .parser import ProjectParser
from .wrapper import MutagenWrapper

db_filepath = os.path.join(
    os.environ.get("MUTAGEN_HELPER_HOME", os.path.join(os.path.expanduser("~"), ".mutagen-helper")), "db.json")


class ManagerInternals:
    def __init__(self):
        self.project_parser = ProjectParser()
        self.wrapper = MutagenWrapper()

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

    def _dispatch_project_files(self, path, dispatcher_function, dispatch_session=False, project_name=None,
                                session_name=None, *args, **kwargs):
        betas = dict()
        for session_info in self.wrapper.list():
            betas[os.path.abspath(os.path.normpath(session_info['Beta']['URL']))] = session_info

        for project_file in scanner.configuration_files(path):
            for project in self.project_parser.parse(project_file):
                for project_session in project['sessions']:
                    betas[os.path.abspath(
                        os.path.normpath(
                            self._effective_beta(project_session, project['project_name'])))] = project_session

        ret = []
        for project_file in scanner.configuration_files(path):
            project_dirname = os.path.abspath(os.path.dirname(os.path.normpath((project_file))))
            for project in self.project_parser.parse(project_file):
                if not project_name or project_name == project['project_name']:
                    if dispatch_session or session_name:
                        for project_session in project['sessions']:
                            if not session_name or session_name == project_session['name']:
                                beta_counterpart = betas.get(project_dirname)
                                if beta_counterpart:
                                    logging.debug("Skip file %s because it match beta of session %s (%s)." % (
                                        project_file, beta_counterpart['project_name'], beta_counterpart['name']))
                                    continue
                                dispatcher_ret = dispatcher_function(project['project_name'], project_session,
                                                                     *args, **kwargs)
                                if dispatcher_ret is not None:
                                    ret.append(dispatcher_ret)
                    else:
                        dispatcher_ret = dispatcher_function(project['project_name'], *args, **kwargs)
                        if dispatcher_ret:
                            ret.extend(dispatcher_ret)

        return ret

    def up(self, path, project_name=None, session_name=None):
        return self._dispatch_project_files(path, self.up_handler, dispatch_session=True, project_name=project_name,
                                            session_name=session_name)

    def up_handler(self, project_name, session):
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

    def down(self, path, project_name=None, session_name=None):
        return self._dispatch_project_files(path, self.down_handler, project_name=project_name,
                                            session_name=session_name)

    def down_handler(self, project_name, session=None):
        session_ids = self.wrapper.terminate(
            label_selector=self._build_label_selector(project_name, name=session['name'] if session else None))
        for session_id in session_ids:
            logging.info('Session %s (%s) terminated.' % (project_name, session_id))
        return session_ids

    def flush(self, path, project_name=None, session_name=None):
        return self._dispatch_project_files(path, self.flush_handler, project_name=project_name,
                                            session_name=session_name)

    def flush_handler(self, project_name, session=None):
        session_ids = self.wrapper.flush(
            label_selector=self._build_label_selector(project_name, name=session['name'] if session else None))
        for session_id in session_ids:
            logging.info('Session %s (%s) flushed.' % (project_name, session_id))
        return session_ids

    def pause(self, path, project_name=None, session_name=None):
        return self._dispatch_project_files(path, self.pause_handler, project_name=project_name,
                                            session_name=session_name)

    def pause_handler(self, project_name, session=None):
        session_ids = self.wrapper.pause(
            label_selector=self._build_label_selector(project_name, name=session['name'] if session else None))
        for session_id in session_ids:
            logging.info('Session %s (%s) paused.' % (project_name, session_id))
        return session_ids

    def resume(self, path, project_name=None, session_name=None):
        return self._dispatch_project_files(path, self.resume_handler, project_name=project_name,
                                            session_name=session_name)

    def resume_handler(self, project_name, session=None):
        session_id = self.wrapper.resume(
            label_selector=self._build_label_selector(project_name, name=session['name'] if session else None))
        logging.info('Session %s (%s) resumed.' % (project_name, session_id))
        return session_id

    def list(self, path, project_name=None, session_name=None, long=False):
        return self._dispatch_project_files(path, self.list_handler, dispatch_session=True, project_name=project_name,
                                            session_name=session_name, long=long)

    def list_handler(self, project_name, session=None, long=False):
        mutagen_session = self.wrapper.list(
            label_selector=self._build_label_selector(project_name, name=session['name'] if session else None),
            long=long,
            one=True)
        if mutagen_session:
            mutagen_session['Mutagen Helper'] = {
                'Project name': project_name,
                'Session name': session.get('name'),
                'Configuration file': session.get('configuration')
            }

        return mutagen_session


class Manager:
    def __init__(self):
        self._internals = ManagerInternals()

    def _sanitize_path(self, path):
        if path:
            return path
        else:
            return os.environ.get('MUTAGEN_HELPER_PATH', os.getcwd())

    def up(self, path=None, project=None, session=None):
        return self._internals.up(self._sanitize_path(path), project_name=project, session_name=session)

    def down(self, path=None, project=None, session=None):
        return self._internals.down(self._sanitize_path(path), project_name=project, session_name=session)

    def resume(self, path=None, project=None, session=None):
        return self._internals.resume(self._sanitize_path(path), project_name=project, session_name=session)

    def pause(self, path=None, project=None, session=None):
        return self._internals.pause(self._sanitize_path(path), project_name=project, session_name=session)

    def list(self, path=None, project=None, session=None, long=False):
        return self._internals.list(self._sanitize_path(path), project_name=project, session_name=session, long=long)

    def flush(self, path=None, project=None, session=None):
        return self._internals.flush(self._sanitize_path(path), project_name=project, session_name=session)

    def project_files(self, path):
        return scanner.configuration_files(self._sanitize_path(path))

    def project_file(self, path):
        return scanner.configuration_file(self._sanitize_path(path))
