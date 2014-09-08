from collections import defaultdict
from collections import namedtuple
import datetime
import errno
import shlex
import os
import re

from . import compat

if compat.ON_WINDOWS:
    import ctypes


PROCFILE_LINE = re.compile(r'^([A-Za-z0-9_]+):\s*(.+)$')


class Env(object):

    def now(self):
        return datetime.datetime.now()

    if compat.ON_WINDOWS:
        # Shamelessly cribbed from
        # https://docs.python.org/2/faq/windows.html#how-do-i-emulate-os-kill-in-windows
        def killpg(self, pid, signum=None):
            """kill function for Win32"""
            kernel32 = ctypes.windll.kernel32
            handle = kernel32.OpenProcess(1, 0, pid)
            return (0 != kernel32.TerminateProcess(handle, 0))
    else:
        def killpg(self, pid, signum=None):
            try:
                os.killpg(pid, signum)
            except OSError as e:
                if e.errno not in [errno.EPERM, errno.ESRCH]:
                    raise


class Procfile(object):
    """A data structure representing a Procfile"""

    def __init__(self):
        self.processes = compat.OrderedDict()

    def add_process(self, name, command):
        assert name not in self.processes, \
            "process names must be unique within a Procfile"
        self.processes[name] = command


def parse_procfile(contents):
    p = Procfile()
    for line in contents.splitlines():
        m = PROCFILE_LINE.match(line)
        if m:
            p.add_process(m.group(1), m.group(2))
    return p


def parse(content):
    """
    Parse the content of a .env file (a line-delimited KEY=value format) into a
    dictionary mapping keys to values.
    """
    values = {}
    for line in content.splitlines():
        m1 = re.match(r'\A([A-Za-z_0-9]+)=(.*)\Z', line)
        if m1:
            key, val = m1.group(1), m1.group(2)
            parts = shlex.split(val, posix=True)
            if len(parts) == 1:
                val = parts[0]
            else:
                val = ' '.join("'%s'" % p for p in parts)
            values[key] = val
    return values


ProcessParams = namedtuple("ProcessParams", "name cmd quiet env")


def expand_processes(processes, concurrency=None, env=None, quiet=None, port=None):
    """
    Get a list of the processes that need to be started given the specified
    list of process types, concurrency, environment, quietness, and base port
    number.

    Returns a list of ProcessParams objects, which have `name`, `cmd`, `env`,
    and `quiet` attributes, corresponding to the parameters to the constructor
    of `honcho.process.Process`.
    """
    if env is not None and env.get("PORT") is not None:
        port = int(env.get("PORT"))

    if port is not None:
        assert port % 1000 == 0, "port must be multiple of 1000"

    if quiet is None:
        quiet = []

    con = defaultdict(lambda: 1)
    if concurrency is not None:
        con.update(concurrency)

    out = []

    for name, cmd in compat.iteritems(processes):
        for i in range(con[name]):
            n = "{0}.{1}".format(name, i + 1)
            c = cmd
            q = name in quiet
            e = {}
            if env is not None:
                e.update(env)
            if port is not None:
                e['PORT'] = str(port + i)

            params = ProcessParams(n, c, q, e)
            out.append(params)
        if port is not None:
            port += 100

    return out
