from __future__ import print_function

import errno
import select
import shlex
import subprocess
import sys
from multiprocessing import Lock

from .colour import get_colours
from .printer import Printer

class Process(subprocess.Popen):
    def __init__(self, *args, **kwargs):
        defaults = {
            'stdout': subprocess.PIPE,
            'stderr': subprocess.PIPE,
            'shell': True
        }
        defaults.update(kwargs)
        super(Process, self).__init__(*args, **defaults)

class ProcessManager(object):
    def __init__(self):
        self.lock = Lock()
        self.processes = []
        self.printers = []
        self.colours = get_colours()

        self.system_printer = Printer(sys.stderr, name='system')

    def add_process(self, name, proc, numprocs=1):
        for i in xrange(1, numprocs+1):
            self.processes.append(('{name}.{i}'.format(**vars()), proc))

    def loop(self):
        self._init_printers()

        for i, proc_tuple in enumerate(self.processes):
            name, proc = proc_tuple
            print("started with pid {}".format(proc.pid), file=self.printers[i][1])

        while [p.poll() for n, p in self.processes].count(None) > 0:
            try:
                try_rlist = [x for n, p in self.processes for x in (p.stdout, p.stderr)]

                try:
                    rlist, _, _ = select.select(try_rlist, [], [])
                except select.error as e:
                    if e.args[0] == errno.EINTR:
                        continue
                    raise

                for i, proc_tuple in enumerate(self.processes):
                    name, proc = proc_tuple
                    if proc.stdout in rlist:
                        self._print_with_lock(proc.stdout, self.printers[i][0])
                    if proc.stderr in rlist:
                        self._print_with_lock(proc.stderr, self.printers[i][1])

            except KeyboardInterrupt:
                print("SIGINT received", file=sys.stderr)
                print("sending SIGTERM to all processes", file=self.system_printer)

                for n, p in self.processes:
                    if p.poll() is None:
                        print("sending SIGTERM to pid {0:d}".format(p.pid), file=self.system_printer)
                        p.terminate()

    def _init_printers(self):
        width = max(len(name) for name, _ in self.processes)
        width = max(width, 6) # 'system'

        self.system_printer.width = width

        for name, proc in self.processes:
            colour = self.colours.next()
            kwargs = dict(name=name, colour=colour, width=width)
            stdout = Printer(sys.stdout, **kwargs)
            stderr = Printer(sys.stderr, **kwargs)
            self.printers.append((stdout, stderr))

    def _print_with_lock(self, fp_in, fp_out):
        l = fp_in.readline()
        if l:
            with self.lock:
                print(l, end='', file=fp_out)
