import datetime
import errno
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

            m2 = re.match(r"\A'(.*)'\Z", val)
            if m2:
                val = m2.group(1)

            m3 = re.match(r'\A"(.*)"\Z', val)
            if m3:
                val = re.sub(r'\\(.)', r'\1', m3.group(1))

            values[key] = val
    return values
