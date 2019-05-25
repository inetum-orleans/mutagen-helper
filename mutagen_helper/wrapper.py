import logging
import os
import re
import shlex
import subprocess
import sys
import time
from queue import Queue, Empty
from threading import Thread

from click import ClickException

mutagen = os.environ.get('MUTAGEN_HELPER_MUTAGEN_BIN', "mutagen.exe" if os.name == 'nt' else "mutagen")


class WrapperException(ClickException):
    pass


class WrapperRunException(WrapperException):
    def __init__(self, *args, **kwargs):
        self.result = kwargs.pop('result')
        super().__init__(*args, **kwargs)


class MutagenRunException(WrapperRunException):
    pass


class DaemonNotRunningException(WrapperRunException):
    pass


class MutagenListParser:
    def _is_separator_line(self, line):
        return line.startswith('-' * 10)

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


class ProcessWrapper:
    STDIN = 0
    STDOUT = 1
    STDERR = 2

    def run(self, command, print_output=False, print_output_if_idle=5000):
        logging.debug('Running command: %s' % shlex.quote(' '.join(command)))

        process = subprocess.Popen(command,
                                   stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   bufsize=1)

        def enqueue_output(process, out, type, queue):
            while True:
                data = out.read(1)
                if data:
                    queue.put((type, data))
                if process.poll() is not None:
                    data = out.read()
                    if data:
                        queue.put((type, data))
                    out.close()
                    break

        def listen_stdin(queue):
            for line in sys.stdin.readline():
                if process.poll() is not None:
                    break
                queue.put((ProcessWrapper.STDIN, line.encode(sys.stdin.encoding)))

        queue = Queue()

        thread = Thread(target=enqueue_output, args=(process, process.stdout, ProcessWrapper.STDOUT, queue))
        thread.daemon = True
        thread.start()

        stderr_thread = Thread(target=enqueue_output, args=(process, process.stderr, ProcessWrapper.STDERR, queue))
        stderr_thread.daemon = True
        stderr_thread.start()

        stdin_thread = Thread(target=listen_stdin, args=(queue,))
        stdin_thread.daemon = True
        stdin_thread.start()

        # read line without blocking
        stdout = b''
        stderr = b''
        stdin = b''

        recorded = []

        last_read_time = int(round(time.time() * 1000))
        while True:
            stream, data = (None, None)
            try:
                stream, data = queue.get_nowait()
                recorded.append((stream, data))
                last_read_time = int(round(time.time() * 1000))
            except Empty:
                if process.stdout.closed and process.stderr.closed:
                    if queue.qsize() == 0:
                        break
                else:
                    if recorded and int(round(time.time() * 1000)) - last_read_time > print_output_if_idle:
                        logging.warning("The following mutagen command seems to require your input: ")
                        logging.warning(shlex.quote(' '.join(command))[1:-1])
                        logging.warning("Please enter your input if required, or kindly wait for it to terminate.")
                        print_output = True
                        for stream, data in recorded:
                            if stream == ProcessWrapper.STDOUT:
                                sys.stdout.buffer.write(data)
                            elif stream == ProcessWrapper.STDERR:
                                sys.stderr.buffer.write(data)
                        recorded = []
                    continue

            if stream == ProcessWrapper.STDOUT:
                stdout = stdout + data
                if print_output:
                    sys.stdout.buffer.write(data)
            elif stream == ProcessWrapper.STDERR:
                stderr = stderr + data
                if print_output:
                    sys.stderr.buffer.write(data)
            elif stream == ProcessWrapper.STDIN:
                stdin = stdin + data
                process.stdin.write(data)
                process.stdin.flush()

        return subprocess.CompletedProcess(process.args, process.returncode,
                                           str(stdout, encoding=sys.stdout.encoding),
                                           str(stderr, encoding=sys.stdout.encoding)
                                           )


class MutagenWrapper(ProcessWrapper):
    def __init__(self, mutagen="mutagen.exe" if os.name == 'nt' else "mutagen"):
        self.mutagen = mutagen
        self.list_parser = MutagenListParser()

    def run(self, command, print_output=False, print_output_on_idle=5000):
        """
        result = subprocess.run([self.mutagen] + command,
                                encoding=sys.stdout.encoding,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
                                """

        result = super().run([self.mutagen] + command, print_output, print_output_on_idle)

        if result.returncode == 1 and 'unable to connect to daemon' in result.stderr:
            raise DaemonNotRunningException("Mutagen daemon doesn't seems to run. "
                                            "Start the daemon with \"mutagen daemon start\" command and try again.",
                                            result=result)

        if result.returncode != 0:
            raise MutagenRunException("Mutagen has failed to execute a command: " +
                                      (shlex.quote(' '.join([self.mutagen] + command))[1:-1]) +
                                      (os.linesep + result.stdout if result.stdout else '') +
                                      (os.linesep + result.stderr if result.stderr else ''),
                                      result=result)

        return result

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

        command = ['create', alpha, beta] + (list(options) if options else [])
        result = self.run(command)
        ret = result.stdout
        match = re.search('Created session\\s(.*?)\\s', ret)
        if match:
            return match.group(1)
        raise WrapperException("Invalid response: " + ret)

    def terminate(self, session_id=None):
        if session_id:
            self.run(['terminate', session_id])
        else:
            self.run(['terminate', '--all'])

    def flush(self, session_id=None):
        if session_id:
            self.run(['flush', session_id])
        else:
            self.run(['flush', '--all'])

    def pause(self, session_id=None):
        if session_id:
            self.run(['pause', session_id])
        else:
            self.run(['pause', '--all'])

    def resume(self, session_id=None):
        if session_id:
            self.run(['resume', session_id])
        else:
            self.run(['resume', '--all'])

    def list(self, session_id=None):
        try:
            if session_id:
                result = self.run(['list', session_id, '-l'])
            else:
                result = self.run(['list', '-l'])
        except MutagenRunException as e:
            if 'unable to locate requested sessions' in e.result.stderr:
                return []
            raise

        output = result.stdout
        return self.list_parser.parse(output)