from __future__ import print_function

import subprocess
import sys
from threading import Thread

try:
    from Queue import Queue, Empty
except ImportError:
    from queue import Queue, Empty # Python 3.x

from .colour import get_colours
from .printer import Printer

ON_POSIX = 'posix' in sys.builtin_module_names

class Process(subprocess.Popen):
    def __init__(self, cmd, name=None, *args, **kwargs):
        self.name = name
        self.reader = None
        self.printer = None

        defaults = {
            'stdout': subprocess.PIPE,
            'stderr': subprocess.STDOUT,
            'shell': True,
            'bufsize': 1,
            'close_fds': ON_POSIX
        }
        defaults.update(kwargs)

        super(Process, self).__init__(cmd, *args, **defaults)

class ProcessManager(object):
    def __init__(self):
        self.processes = []
        self.colours = get_colours()

        self._terminating = False

        self.system_printer = Printer(sys.stdout, name='system')

    def add_process(self, name, cmd, concurrency=1):
        for i in xrange(1, concurrency + 1):
            n = '{name}.{i}'.format(**vars())
            self.processes.append(Process(cmd, name=n))

    def loop(self):
        self._init_readers()
        self._init_printers()

        for proc in self.processes:
            print("started with pid {}".format(proc.pid), file=proc.printer)

        while self._process_count() > 0:
            try:
                for proc in self.processes:

                    try:
                        line = proc.reader.get_nowait()
                    except Empty:
                        pass
                    else:
                        print(line, end='', file=proc.printer)

                    if proc.poll() is not None:
                        print('process terminated', file=proc.printer)
                        self.processes.remove(proc)
                        self.terminate()

            except KeyboardInterrupt:
                print("SIGINT received", file=sys.stderr)
                self.terminate()


    def terminate(self):
        if self._terminating:
            return False

        self._terminating = True

        print("sending SIGTERM to all processes", file=self.system_printer)
        for proc in self.processes:
            if proc.poll() is None:
                print("sending SIGTERM to pid {0:d}".format(proc.pid), file=self.system_printer)
                proc.terminate()

    def _process_count(self):
        return [p.poll() for p in self.processes].count(None)

    def _init_readers(self):
        for proc in self.processes:
            q = Queue()
            t = Thread(target=enqueue_output, args=(proc.stdout, q))
            t.daemon = True # thread dies with the program
            t.start()
            proc.reader = q

    def _init_printers(self):
        width = max(len(p.name) for p in self.processes)
        width = max(width, len(self.system_printer.name))

        self.system_printer.width = width

        for proc in self.processes:
            proc.printer = Printer(sys.stdout,
                                   name=proc.name,
                                   colour=self.colours.next(),
                                   width=width)

def enqueue_output(out, queue):
    for line in iter(out.readline, b''):
        queue.put(line)
    out.close()
