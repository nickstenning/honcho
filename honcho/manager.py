import datetime
import multiprocessing
import signal
import sys

from .colour import get_colours
from .compat import Empty
from .compat import iteritems
from .environ import Env
from .process import Process
from .printer import Printer, Message

KILL_WAIT = 5
SIGNALS = {
    signal.SIGINT: {
        'name': 'SIGINT',
        'rc': 130,
    },
    signal.SIGTERM: {
        'name': 'SIGTERM',
        'rc': 143,
    },
}
SYSTEM_PRINTER_NAME = 'system'


class Manager(object):
    """
    Manager is responsible for running multiple external processes in parallel
    managing the events that result (starting, stopping, printing). By default
    it relays printed lines to a printer that prints to STDOUT.

    Example:

        m = Manager()
        m.add_process('server', 'ruby server.rb')
        m.add_process('worker', 'python worker.py')
        m.loop()
    """

    def __init__(self, printer=None):
        self.events = multiprocessing.Queue()
        self.returncode = None

        self._colours = get_colours()
        self._env = Env()

        self._printer = printer if printer is not None else Printer(sys.stdout)
        self._printer.width = len(SYSTEM_PRINTER_NAME)

        self._process_ctor = Process
        self._processes = {}

        self._terminating = False

    def add_process(self, name, cmd, quiet=False, env=None):
        """
        Add a process to this manager instance. The process will not be started
        until #loop() is called.
        """
        assert name not in self._processes, "process names must be unique"
        proc = self._process_ctor(cmd,
                                  name=name,
                                  quiet=quiet,
                                  colour=next(self._colours),
                                  env=env)
        self._processes[name] = {}
        self._processes[name]['obj'] = proc

        # Update printer width to accommodate this process name
        self._printer.width = max(self._printer.width, len(name))

        return proc

    def loop(self):
        """
        Start all the added processes and multiplex their output onto the bound
        printer (which by default will print to STDOUT).

        If one process terminates, all the others will be terminated by
        Honcho, and #loop() will return.

        This method will block until all the processes have terminated.
        """
        def _terminate(signum, frame):
            self._system_print("%s received\n" % SIGNALS[signum]['name'])
            self.returncode = SIGNALS[signum]['rc']
            self.terminate()

        signal.signal(signal.SIGTERM, _terminate)
        signal.signal(signal.SIGINT, _terminate)

        self._start()

        exit = False
        exit_start = None

        while 1:
            try:
                msg = self.events.get(timeout=0.1)
            except Empty:
                if exit:
                    break
            else:
                if msg.type == 'line':
                    self._printer.write(msg)
                elif msg.type == 'start':
                    self._processes[msg.name]['pid'] = msg.data['pid']
                    self._system_print("%s started (pid=%s)\n"
                                       % (msg.name, msg.data['pid']))
                elif msg.type == 'stop':
                    self._processes[msg.name]['returncode'] = msg.data['returncode']
                    self._system_print("%s stopped (rc=%s)\n"
                                       % (msg.name, msg.data['returncode']))
                    if self.returncode is None:
                        self.returncode = msg.data['returncode']

            if self._all_started() and self._all_stopped():
                exit = True

            if exit_start is None and self._all_started() and self._any_stopped():
                exit_start = self._env.now()
                self.terminate()

            if exit_start is not None:
                # If we've been in this loop for more than KILL_WAIT seconds,
                # it's time to kill all remaining children.
                waiting = self._env.now() - exit_start
                if waiting > datetime.timedelta(seconds=KILL_WAIT):
                    self.kill()

    def terminate(self):
        """
        Terminate all processes managed by this ProcessManager.
        """
        if self._terminating:
            return
        self._terminating = True
        self._killall()

    def kill(self):
        """
        Kill all processes managed by this ProcessManager.
        """
        self._killall(force=True)

    def _killall(self, force=False):
        """Kill all remaining processes, forcefully if requested."""
        for_termination = []

        for n, p in iteritems(self._processes):
            if 'returncode' not in p:
                for_termination.append(n)

        for n in for_termination:
            p = self._processes[n]
            signame = 'SIGKILL' if force else 'SIGTERM'
            self._system_print("sending %s to %s (pid %s)\n" %
                               (signame, n, p['pid']))
            if force:
                self._env.kill(p['pid'])
            else:
                self._env.terminate(p['pid'])

    def _start(self):
        for name, p in self._processes.items():
            p['process'] = multiprocessing.Process(name=name,
                                                   target=p['obj'].run,
                                                   args=(self.events, True))
            p['process'].start()

    def _all_started(self):
        return all(p.get('pid') is not None for _, p in iteritems(self._processes))

    def _all_stopped(self):
        return all(p.get('returncode') is not None for _, p in iteritems(self._processes))

    def _any_stopped(self):
        return any(p.get('returncode') is not None for _, p in iteritems(self._processes))

    def _system_print(self, data):
        self._printer.write(Message(type='line',
                                    data=data,
                                    time=self._env.now(),
                                    name=SYSTEM_PRINTER_NAME,
                                    colour=None))
