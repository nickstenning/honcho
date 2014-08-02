from __future__ import print_function

import signal
import subprocess
import sys
from threading import Thread

from .colour import get_colours
from .compat import ON_WINDOWS
from .compat import Queue, Empty
from .printer import Printer

SYSTEM_PRINTER_NAME = "system"


class Process(object):
    """

    A simple utility wrapper around subprocess.Popen that stores
    a number of attributes needed by Honcho.

    """
    def __init__(self,
                 cmd,
                 name=None,
                 quiet=False,
                 popen=subprocess.Popen,
                 *args,
                 **kwargs):

        self.name = name
        self.quiet = quiet
        self.dead = False

        self._popen = popen

        if self.quiet:
            self.name = "{0} (quiet)".format(self.name)

        defaults = {
            'stdout': subprocess.PIPE,
            'stderr': subprocess.STDOUT,
            'shell': True,
            'bufsize': 1,
            'close_fds': not ON_WINDOWS
        }
        defaults.update(kwargs)

        self.proc = self._popen(cmd, *args, **defaults)

    def poll(self):
        return self.proc.poll()

    def kill(self):
        return self.proc.kill()

    def terminate(self):
        return self.proc.terminate()

    def wait(self):
        return self.proc.wait()

    @property
    def pid(self):
        return self.proc.pid

    @property
    def returncode(self):
        return self.proc.returncode

    @property
    def stdout(self):
        return self.proc.stdout

    @property
    def stderr(self):
        return self.proc.stderr

    @property
    def stdin(self):
        return self.proc.stdin


class ProcessManager(object):
    """

    Here's where the business happens. The ProcessManager multiplexes and
    pretty-prints the output from a number of Process objects, typically added
    using the add_process() method.

    Example:

        pm = ProcessManager()
        pm.add_process('name', 'ruby server.rb')
        pm.add_process('name', 'python worker.py')

        pm.loop()

    """

    def __init__(self, printer=None, process=Process):
        self.returncode = None

        self._colours = get_colours()
        self._printer = printer if printer is not None else Printer(sys.stdout)
        self._printer.width = max(self._printer.width,
                                  len(SYSTEM_PRINTER_NAME))
        self._process = process
        self._processes = []
        self._queue = Queue()
        self._terminating = False

    def add_process(self, name, cmd, quiet=False):
        """

        Add a process to this manager instance:

        Arguments:

        name        - a human-readable identifier for the process
                      (e.g. 'worker'/'server')
        cmd         - the command-line used to run the process
                      (e.g. 'python run.py')

        """
        proc = self._process(cmd, name=name, quiet=quiet)
        proc.colour = next(self._colours)
        self._printer.width = max(self._printer.width, len(proc.name))
        self._processes.append(proc)
        return proc

    def loop(self):
        """

        Enter the main loop of the program. This will print the multiplexed
        output of all the processes in this ProcessManager to sys.stdout, and
        will block until all the processes have completed.

        If one process terminates, all the others will be terminated by
        Honcho, and loop() will return.

        Returns: the returncode of the first process to exit, or 130 if
        interrupted with Ctrl-C (SIGINT)

        """

        self._init_readers()

        for proc in self._processes:
            self._print("started with pid {0}\n".format(proc.pid), process=proc)

        while True:
            try:
                proc, line = self._queue.get(timeout=0.1)
            except Empty:
                pass
            except KeyboardInterrupt:
                print("SIGINT received", file=sys.stderr)
                self.returncode = 130
                self.terminate()
            else:
                self._print(line, process=proc)

            for proc in self._processes:
                if not proc.dead and proc.poll() is not None:
                    self._print('process terminated\n', process=proc)
                    proc.dead = True

                    # Set the returncode of the ProcessManager instance if not
                    # already set.
                    if self.returncode is None:
                        self.returncode = proc.returncode

                    self.terminate()

            if not self._process_count() > 0:
                break

        while True:
            try:
                proc, line = self._queue.get(timeout=0.1)
            except Empty:
                break
            else:
                self._print(line, process=proc)

        return self.returncode

    def terminate(self, kill_fallback=True):
        """

        Terminate all the child processes of this ProcessManager, bringing the
        loop() to an end.

        """
        if self._terminating:
            return False

        self._terminating = True

        self._print("sending SIGTERM to all processes")
        for proc in self._processes:
            if proc.poll() is None:
                self._print("sending SIGTERM to pid {0:d}".format(proc.pid))
                proc.terminate()

        def kill(signum, frame):
            # If anything is still alive, SIGKILL it
            for proc in self._processes:
                if proc.poll() is None:
                    self._print("sending SIGKILL to pid {0:d}".format(proc.pid))
                    proc.kill()

        if kill_fallback:
            if ON_WINDOWS:
                # SIGALRM is not supported on Windows: just kill instead
                kill(None, None)
            else:
                # the default is POSIX
                signal.signal(signal.SIGALRM, kill)  # @UndefinedVariable
                signal.alarm(5)  # @UndefinedVariable

    def _process_count(self):
        return [p.poll() for p in self._processes].count(None)

    def _init_readers(self):
        for proc in self._processes:
            t = Thread(target=_enqueue_output, args=(proc, self._queue))
            t.daemon = True  # thread dies with the program
            t.start()

    def _print(self, string, process=None):
        if process is None:
            self._printer.write(string, name=SYSTEM_PRINTER_NAME)
        else:
            if isinstance(string, UnicodeDecodeError):
                self._print("UnicodeDecodeError while decoding line from "
                            "process {0:s}\n" .format(process.name))
                return
            self._printer.write(string, name=process.name, colour=process.colour)


def _enqueue_output(proc, queue):
    for line in iter(proc.stdout.readline, b''):
        if not proc.quiet:
            try:
                line = line.decode('utf-8')
            except UnicodeDecodeError as e:
                queue.put((proc, e))
                continue
            queue.put((proc, line))
    proc.stdout.close()
