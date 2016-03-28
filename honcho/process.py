from __future__ import print_function

import os
import signal
import subprocess
import sys

from .compat import ON_WINDOWS
from .environ import Env
from .printer import Message


class Process(object):
    """
    A simple utility wrapper around a subprocess.Popen that stores
    a number of attributes needed by Honcho and supports forwarding process
    lifecycle events and output to a queue.
    """
    def __init__(self,
                 cmd,
                 name=None,
                 colour=None,
                 quiet=False,
                 env=None,
                 cwd=None):
        self.cmd = cmd
        self.colour = colour
        self.quiet = quiet
        self.name = name
        self.env = os.environ.copy() if env is None else env
        self.cwd = cwd

        # This is a honcho.environ.Env object, to allow for stubbing of
        # external calls, not the operating system environment.
        self._env = Env()
        self._child = None
        self._child_ctor = Popen

    def run(self, events=None, ignore_signals=False):
        self._events = events
        self._child = self._child_ctor(self.cmd, env=self.env, cwd=self.cwd)
        self._send_message({'pid': self._child.pid}, type='start')

        # Don't pay attention to SIGINT/SIGTERM. The process itself is
        # considered unkillable, and will only exit when its child (the shell
        # running the Procfile process) exits.
        if ignore_signals:
            signal.signal(signal.SIGINT, signal.SIG_IGN)
            signal.signal(signal.SIGTERM, signal.SIG_IGN)

        for line in iter(self._child.stdout.readline, b''):
            if not self.quiet:
                self._send_message(line)
        self._child.stdout.close()
        self._child.wait()

        self._send_message({'returncode': self._child.returncode}, type='stop')

    def _send_message(self, data, type='line'):
        if self._events is not None:
            self._events.put(Message(type=type,
                                     data=data,
                                     time=self._env.now(),
                                     name=self.name,
                                     colour=self.colour))


class Popen(subprocess.Popen):

    def __init__(self, cmd, **kwargs):
        start_new_session = kwargs.pop('start_new_session', True)
        options = {
            'stdout': subprocess.PIPE,
            'stderr': subprocess.STDOUT,
            'shell': True,
            'bufsize': 1,
            'close_fds': not ON_WINDOWS,
        }
        options.update(**kwargs)

        if ON_WINDOWS:
            # MSDN reference:
            #   http://msdn.microsoft.com/en-us/library/windows/desktop/ms684863%28v=vs.85%29.aspx
            create_new_process_group = 0x00000200
            detached_process = 0x00000008
            options.update(creationflags=detached_process | create_new_process_group)
        elif start_new_session:
            if sys.version_info < (3, 2):
                options.update(preexec_fn=os.setsid)
            else:
                options.update(start_new_session=True)

        super(Popen, self).__init__(cmd, **options)
