import logging
import os

from tinydb import TinyDB, Query

from .parser import YamlProjectParser
from .wrapper import MutagenWrapper

db_filepath = os.path.join(
    os.environ.get("MUTAGEN_HELPER_HOME", os.path.join(os.path.expanduser("~"), ".mutagen-helper")), "db.json")


class ManagerException(Exception):
    pass


class ManagerInternals:
    def __init__(self, purge=False, filepath=db_filepath):
        self.project_parser = YamlProjectParser()
        self.wrapper = MutagenWrapper()
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        self.db = TinyDB(filepath, default_table='sessions')
        if purge:
            self.db.purge_tables()
        self.db.table('sessions', cache_size=0)

    def _append_project_name_to_beta(self, session, project_name):
        beta = session['beta']
        if session['append_project_name_to_beta']:
            sep = '/'
            if beta.endswith('/') or beta.endswith('\\'):
                sep = ''
            beta = beta + sep + project_name
        session['beta'] = beta

    def _effective_beta(self, session, project_name):
        beta = session['beta']
        if session['append_project_name_to_beta'] \
                and not beta.endswith('/' + project_name) and not beta.endswith('\\' + project_name):
            if beta.endswith('/') or beta.endswith('\\'):
                beta = beta + project_name
            beta = beta + '/' + project_name
        return beta

    def _get_db_session(self, session, project_name, build_if_not_found=False):
        if hasattr(session, 'doc_id'):
            return session

        name = session['name']
        db_session = None

        db_sessions = self.db.search(self._build_session_condition(session))
        if db_sessions:
            if len(db_sessions) > 1:
                raise ManagerException("Too many matching sessions")
            for db_session_candidate in db_sessions:
                db_session_id = db_session_candidate.get('session_id')
                if not db_session_id or not self.wrapper.list(db_session_id):
                    # Invalid session in database
                    logging.warning("Session %s found in mutagen-helper, but doesn't exists in mutagen. "
                                    "Removing from mutagen-helper." % db_session_id)
                    self.db.remove(doc_ids=[db_session_candidate.doc_id])
                else:
                    db_session = db_session_candidate
                    break

        if not db_session and build_if_not_found:
            alpha = session['alpha']
            beta = self._effective_beta(session, project_name)
            db_session = self._build_db_session(project_name, name, alpha, beta, session.get('options'))
        return db_session

    def _build_db_session(self, project_name, name, alpha, beta, options=None, session_id=None):
        return {
            'project_name': project_name,
            'alpha': alpha,
            'beta': beta,
            'name': name,
            'options': options,
            'session_id': session_id
        }

    def _build_session_condition(self, session):
        query = Query()
        return (query.project_name == session['project_name']) & (query.name == session['name'])

    def _session_has_changed(self, db_session, session, project_name):
        return db_session['alpha'] != session['alpha'] or \
               db_session['beta'] != self._effective_beta(session, project_name) or \
               db_session['options'] != session['options']

    def _dispatch_project_files(self, path, dispatcher_function):
        betas = dict()
        for db_session in self.db.all():
            betas[os.path.abspath(os.path.normpath(db_session['beta']))] = db_session

        for project_file in self.project_files(path):
            project = self.project_parser.parse(project_file)
            project_name = project['project_name']
            for session in project['sessions']:
                betas[os.path.abspath(os.path.normpath(self._effective_beta(session, project_name)))] = session

        ret = []
        for project_file in self.project_files(path):
            project = self.project_parser.parse(project_file)
            project_name = project['project_name']
            for session in project['sessions']:
                beta_counterpart = betas.get(os.path.abspath(os.path.dirname(os.path.normpath((project_file)))))
                if beta_counterpart:
                    logging.debug("Skip file %s because it match beta of session %s (%s)." % (
                        project_file, beta_counterpart['project_name'], beta_counterpart['name']))
                    continue
                dispatcher_ret = dispatcher_function(session, project_name)
                if dispatcher_ret is not None:
                    ret.append(dispatcher_ret)

        return ret

    def up(self, path):
        return self._dispatch_project_files(path, self.up_session)

    def up_session(self, session, project_name):
        db_session = self._get_db_session(session, project_name, build_if_not_found=True)

        name = session['name']
        session_id = db_session.get('session_id')
        options = session.get('options')

        if session_id and self.wrapper.list(session_id):
            if self._session_has_changed(db_session, session, project_name):
                logging.info(
                    'Session %s[%s] (%s) exists, but its configuration for has changed.' % (
                        project_name, name, session_id))
            else:
                logging.debug('Session %s[%s] (%s) already exists.' % (project_name, name, session_id))
                return
        else:
            logging.debug('No session %s[%s] found.' % (name, project_name))

        session_id = self.wrapper.create(db_session['alpha'], db_session['beta'], db_session.get('options'))
        logging.info('Session %s[%s] (%s) created.' % (project_name, name, session_id))

        db_session['session_id'] = session_id
        db_session['options'] = options
        db_session['project_name'] = project_name
        if hasattr(db_session, 'doc_id'):
            self.db.upsert(db_session, doc_ids=[db_session.doc_id])
        else:
            db_session['doc_id'] = self.db.insert(db_session)

        return db_session

    def down(self, path):
        return self._dispatch_project_files(path, self.down_session)

    def down_session(self, session, project_name):
        db_session = self._get_db_session(session, project_name)
        if not db_session or not db_session.get('session_id'):
            logging.warning('Session %s[%s] is not available.' % (project_name, session['name']))
            return

        self.wrapper.terminate(db_session['session_id'])
        logging.info('Session %s[%s] (%s) terminated.' % (project_name, session['name'], db_session['session_id']))

        if hasattr(db_session, 'doc_id'):
            self.db.remove(doc_ids=[db_session.doc_id])

        return db_session

    def flush(self, path):
        return self._dispatch_project_files(path, self.flush_session)

    def flush_session(self, session, project_name):
        db_session = self._get_db_session(session, project_name)
        if not db_session or not db_session.get('session_id'):
            logging.warning('Session %s[%s] is not available.' % (project_name, session['name']))
            return

        self.wrapper.flush(db_session['session_id'])
        logging.info('Session %s[%s] (%s) flushed.' % (project_name, session['name'], db_session['session_id']))

        return db_session

    def pause(self, path):
        return self._dispatch_project_files(path, self.pause_session)

    def pause_session(self, session, project_name):
        db_session = self._get_db_session(session, project_name)
        if not db_session or not db_session.get('session_id'):
            logging.warning('Session %s[%s] is not available.' % (project_name, session['name']))
            return

        self.wrapper.pause(db_session['session_id'])
        logging.info('Session %s[%s] (%s) paused.' % (project_name, session['name'], db_session['session_id']))
        return db_session

    def resume(self, path):
        return self._dispatch_project_files(path, self.resume_session)

    def resume_session(self, session, project_name):
        db_session = self._get_db_session(session, project_name)
        if not db_session or not db_session.get('session_id'):
            logging.warning('Session %s[%s] is not available.' % (project_name, session['name']))
            return

        self.wrapper.resume(db_session['session_id'])
        logging.info('Session %s[%s] (%s) resumed.' % (project_name, session['name'], db_session['session_id']))
        return db_session

    def project_file(self, path):
        candidates = ['.mutagen.yml', '.mutagen.yaml']
        for candidate in candidates:
            candidate_path = os.path.join(path, candidate)
            if os.path.isfile(os.path.join(path, candidate)):
                return candidate_path
        return

    def list(self, path):
        return self._dispatch_project_files(path, self.list_session)

    def list_session(self, session, project_name):
        db_session = self._get_db_session(session, project_name)
        if not db_session or not db_session.get('session_id'):
            logging.warning('Session %s[%s] is not available.' % (project_name, session['name']))
            return

        mutagen_sessions = self.wrapper.list(db_session['session_id'])
        if not mutagen_sessions:
            return

        mutagen_session = mutagen_sessions[0]
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
