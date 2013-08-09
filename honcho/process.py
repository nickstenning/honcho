from __future__ import print_function

import signal
import subprocess
import sys
from threading import Thread

try:
    from Queue import Queue, Empty
except ImportError:
    from queue import Queue, Empty  # Python 3.x

from .colour import get_colours
from .printer import Printer
from .compat import ON_WINDOWS


class Process(subprocess.Popen):
    """

    A simple utility wrapper around subprocess.Popen that stores
    a number of attributes needed by Honcho.

    """
    def __init__(self, cmd, name=None, quiet=False, *args, **kwargs):
        self.name = name
        self.quiet = quiet
        self.reader = None
        self.printer = None
        self.dead = False

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

        super(Process, self).__init__(cmd, *args, **defaults)


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
    def __init__(self):
        self.processes = []
        self.colours = get_colours()
        self.queue = Queue()
        self.system_printer = Printer(sys.stdout, name='system')
        self.returncode = None

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
        self.processes.append(Process(cmd, name=name, quiet=quiet))

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
        self._init_printers()

        for proc in self.processes:
            print("started with pid {0}".format(proc.pid), file=proc.printer)

        while True:
            try:
                proc, line = self.queue.get(timeout=0.1)
            except Empty:
                pass
            except KeyboardInterrupt:
                print("SIGINT received", file=sys.stderr)
                self.returncode = 130
                self.terminate()
            else:
                print(line, end='', file=proc.printer)

            for proc in self.processes:
                if not proc.dead and proc.poll() is not None:
                    print('process terminated', file=proc.printer)
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
                proc, line = self.queue.get(timeout=0.1)
            except Empty:
                break
            else:
                print(line, end='', file=proc.printer)

        return self.returncode

    def terminate(self):
        """

        Terminate all the child processes of this ProcessManager, bringing the
        loop() to an end.

        """
        if self._terminating:
            return False

        self._terminating = True

        print("sending SIGTERM to all processes", file=self.system_printer)
        for proc in self.processes:
            if proc.poll() is None:
                print("sending SIGTERM to pid {0:d}".format(proc.pid), file=self.system_printer)
                proc.terminate()

        def kill(signum, frame):
            # If anything is still alive, SIGKILL it
            for proc in self.processes:
                if proc.poll() is None:
                    print("sending SIGKILL to pid {0:d}".format(proc.pid), file=self.system_printer)
                    proc.kill()

        if ON_WINDOWS:
            # SIGALRM is not supported on Windows: just kill instead
            kill(None, None)
        else:
            # the default is POSIX
            signal.signal(signal.SIGALRM, kill) # @UndefinedVariable
            signal.alarm(5) # @UndefinedVariable

    def _process_count(self):
        return [p.poll() for p in self.processes].count(None)

    def _init_readers(self):
        for proc in self.processes:
            t = Thread(target=_enqueue_output, args=(proc, self.queue))
            t.daemon = True  # thread dies with the program
            t.start()

    def _init_printers(self):
        width = max(len(p.name) for p in filter( lambda x: not x.quiet, self.processes))
        width = max(width, len(self.system_printer.name))

        self.system_printer.width = width

        for proc in self.processes:
            proc.printer = Printer(sys.stdout,
                                   name=proc.name,
                                   colour=next(self.colours),
                                   width=width)


def _enqueue_output(proc, queue):
    if not proc.quiet:
        for line in iter(proc.stdout.readline, b''):
            line = line.decode('utf-8')
            if not line.endswith('\n'):
                line += '\n'
            queue.put((proc, line))
        proc.stdout.close()
