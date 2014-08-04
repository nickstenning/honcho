import datetime
import errno
import os
import re

from .compat import ON_WINDOWS

if ON_WINDOWS:
    import ctypes


class Env(object):

    def now(self):
        return datetime.datetime.now()

    if ON_WINDOWS:
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
