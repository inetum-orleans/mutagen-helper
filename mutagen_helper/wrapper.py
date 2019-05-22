import os
import re
import shlex
import subprocess
import sys


mutagen = os.environ.get('MUTAGEN_HELPER_MUTAGEN_BIN', "mutagen.exe" if os.name == 'nt' else "mutagen")


class WrapperException(Exception):
    pass


class MutagenListParser:
    def _is_separator_line(self, line):
        return line.startswith('-'*10)

    def parse(self, output: str):
        if not output:
            return []
        lines = output.splitlines()
        if not self._is_separator_line(lines[0]):
            raise
        del lines[0]
        stack = [{}]
        sessions = []
        previous_key = None
        for line in lines:
            if self._is_separator_line(line):
                sessions.append(stack[0])
                previous_key = None
                current_session = {}
                stack = [current_session]
            else:
                if ':' in line:
                    key, value = line.split(":", 1)

                    stack_size = key.count('\t') + 1
                    key = key.strip()
                    value = value.strip()
                    if stack_size == len(stack) + 1:
                        current_object = {}
                        if stack[-1][previous_key]:
                            raise WrapperException("Invalid structure for mutagen output")
                        stack[-1][previous_key] = current_object
                        stack.append(current_object)
                    else:
                        stack = stack[:stack_size]
                    stack[-1][key] = value
                    previous_key = key
                else:
                    value = line

                    stack_size = value.count('\t') + 1
                    value = value.strip()

                    if stack_size == len(stack) + 1:
                        current_object = []
                        if stack[-1][previous_key]:
                            raise WrapperException("Invalid structure for mutagen output")
                        stack[-1][previous_key] = current_object
                        stack.append(current_object)
                    else:
                        stack = stack[:stack_size]

                    if isinstance(current_object, list):
                        current_object.append(value)
                    else:
                        raise WrapperException("Invalid structure for mutagen output")
        return sessions


class MutagenWrapper:
    def __init__(self, mutagen="mutagen.exe" if os.name == 'nt' else "mutagen"):
        self.mutagen = mutagen
        self.list_parser = MutagenListParser()

    def create(self, alpha, beta, options=None):
        """
        Creates a new session

        :param alpha:
        :param beta:
        :param options:
        :return:
        """
        if isinstance(options, dict):
            options_list = []
            for k, v in options.items():
                if v:
                    if isinstance(v, list):
                        for item in v:
                            options_list.append('--' + str(k))
                            options_list.append(str(item))
                    else:
                        options_list.append('--' + str(k))
                        if not isinstance(v, bool):
                            options_list.append(str(v))
            options = options_list
        elif isinstance(options, str):
            options = shlex.split(options)

        result = self.run([self.mutagen, 'create', alpha, beta] + (list(options) if options else []))
        ret = result.stdout
        match = re.search('Created session\\s(.*?)\\s', ret)
        if match:
            return match.group(1)
        raise WrapperException("Invalid response: " + ret)

    def run(self, command):
        return subprocess.run(command, check=True,
                              encoding=sys.stdout.encoding,
                              stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE)

    def terminate(self, session_id=None):
        if session_id:
            self.run([self.mutagen, 'terminate', session_id])
        else:
            self.run([self.mutagen, 'terminate', '--all'])

    def flush(self, session_id=None):
        if session_id:
            self.run([self.mutagen, 'flush', session_id])
        else:
            self.run([self.mutagen, 'flush', '--all'])

    def pause(self, session_id=None):
        if session_id:
            self.run([self.mutagen, 'pause', session_id])
        else:
            self.run([self.mutagen, 'pause', '--all'])

    def resume(self, session_id=None):
        if session_id:
            self.run([self.mutagen, 'resume', session_id])
        else:
            self.run([self.mutagen, 'resume', '--all'])

    def list(self, session_id=None):
        try:
            if session_id:
                result = self.run([self.mutagen, 'list', session_id, '-l'])
            else:
                result = self.run([self.mutagen, 'list', '-l'])
        except subprocess.CalledProcessError as e:
            if e.returncode == 1 and 'unable to locate requested sessions' in e.stderr:
                return []
            raise

        output = result.stdout
        return self.list_parser.parse(output)
