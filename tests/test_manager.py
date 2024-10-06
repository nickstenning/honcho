import datetime
import multiprocessing
import queue

import pytest

from honcho.manager import SYSTEM_PRINTER_NAME, Manager
from honcho.printer import Message

HISTORIES = {
    'one': {
        'processes': {'foo': {}},
        'messages': (('foo', 'start', {'pid': 123}),
                     ('foo', 'line', b'hello, world!\n'),
                     ('foo', 'stop', {'returncode': 0})),
    },
    'two': {
        'processes': {'bar': {}, 'foo': {}},
        'messages': (('foo', 'start', {'pid': 123}),
                     ('bar', 'start', {'pid': 124}),
                     ('foo', 'line', b'process one\n'),
                     ('bar', 'line', b'process two\n'),
                     ('foo', 'stop', {'returncode': 0}),
                     ('bar', 'stop', {'returncode': 0})),
    },
    'returncode': {
        'processes': {'bar': {}, 'foo': {}},
        'messages': (('foo', 'start', {'pid': 123}),
                     ('bar', 'start', {'pid': 124}),
                     ('foo', 'stop', {'returncode': 456}),
                     ('bar', 'stop', {'returncode': 321})),
    },
    'output_after_stop': {
        'processes': {'bar': {}, 'foo': {}},
        'messages': (('foo', 'start', {'pid': 123}),
                     ('bar', 'start', {'pid': 124}),
                     ('foo', 'line', b'hi from foo\n'),
                     ('bar', 'line', b'hi from bar\n'),
                     ('foo', 'stop', {'returncode': 0}),
                     ('bar', 'line', b'fishmongers\n'),
                     ('bar', 'line', b'butchers\n'),
                     ('bar', 'stop', {'returncode': -15})),
    },
}


class FakeClock(object):

    def now(self):
        return datetime.datetime(2012, 8, 11, 12, 42)


class FakeProcessManager(object):

    def terminate(self, pid):
        pass

    def kill(self, pid):
        pass


class FakeProcess(object):

    def __init__(self, cmd, name=None, colour=None, quiet=None, env=None, cwd=None):
        self.cmd = cmd
        self.name = name
        self.colour = colour
        self.quiet = quiet
        self.env = env
        self.cwd = cwd

        self._events = None
        self._options = {}

    def run(self, events=None, ignore_signals=False):
        self._report('run', events_passed=events is not None)

    def _report(self, type, **data):
        if self._events is not None:
            data.update({'type': type,
                         'name': self.name})
            self._events.put(data)


class Harness(object):

    def __init__(self, history, manager):
        self.history = history
        self.manager = manager
        self.events_local = []

        self._q = multiprocessing.Queue()
        self._rc = multiprocessing.Value('i', -999)

    def run(self, wait=True):
        self.manager._process_ctor = self._process_ctor

        for name, options in self.history['processes'].items():
            self.manager.add_process(name,
                                     options.get('command', 'test'),
                                     options.get('quiet', False))

        def _loop(rc):
            self.manager.loop()
            rc.value = self.manager.returncode

        self._mproc = multiprocessing.Process(target=_loop, args=(self._rc,))
        self._mproc.start()

        for msg in self.history['messages']:
            self.send_manager(*msg)

        self._mproc.join()

    @property
    def manager_returncode(self):
        if self._rc.value == -999:
            return None
        return self._rc.value

    def send_manager(self, process_name, type, data, **kwargs):
        self.manager.events.put(Message(type=type,
                                        data=data,
                                        time=datetime.datetime.now(),
                                        name=process_name,
                                        colour=None))

    def fetch_events(self):
        """
        Retrieve any pending events from the queue and put them on the local
        event cache
        """
        while 1:
            try:
                self.events_local.append(self._q.get(False))
            except queue.Empty:
                break

    def find_events(self, name=None, type=None):
        self.fetch_events()
        results = []
        for event in self.events_local:
            if name is not None and event['name'] != name:
                continue
            if type is not None and event['type'] != type:
                continue
            results.append(event)
        return results

    def _process_ctor(self, *args, **kwargs):
        options = self.history['processes'][kwargs['name']]
        p = FakeProcess(*args, **kwargs)
        p._events = self._q
        p._options = options
        return p


class FakePrinter(object):

    def __init__(self, width=0):
        self.width = width
        self.lines_local = []

        self._q = multiprocessing.Queue()

    def write(self, message):
        # Called in a remote thread, so just put the message on the queue.
        self._q.put(message)

    def fetch_lines(self):
        """
        Retrieve any pending lines from the queue and put them on the local
        line cache
        """
        while 1:
            try:
                self.lines_local.append(self._q.get(False))
            except queue.Empty:
                break

    def got_line(self, data):
        return self.find_line(data) is not None

    def find_line(self, data):
        self.fetch_lines()
        for line in self.lines_local:
            if line.data == data:
                return line


class TestManager(object):
    @pytest.fixture(autouse=True)
    def printer(self):
        self.p = FakePrinter()
        self.m = Manager(printer=self.p)
        self.m._clock = FakeClock()
        self.m._procmgr = FakeProcessManager()

    def run_history(self, name, wait=True):
        self.h = Harness(HISTORIES[name], self.m)
        self.h.run(wait=wait)

    def test_init_sets_default_printer_width(self):
        assert self.p.width == len(SYSTEM_PRINTER_NAME)

    def test_add_process_updates_printer_width(self):
        self.m.add_process('interesting', 'ruby server.rb')
        assert self.p.width == len('interesting')

    def test_add_process_sets_name(self):
        proc = self.m.add_process('foo', 'ruby server.rb')
        assert proc.name == 'foo'

    def test_add_process_sets_cmd(self):
        proc = self.m.add_process('foo', 'ruby server.rb')
        assert proc.cmd == 'ruby server.rb'

    def test_add_process_sets_colour(self):
        proc = self.m.add_process('foo', 'ruby server.rb')
        assert proc.colour is not None

    def test_add_process_sets_unique_colours(self):
        p1 = self.m.add_process('foo', 'ruby server.rb')
        p2 = self.m.add_process('bar', 'python server.py')
        assert p1.colour != p2.colour

    def test_add_process_sets_quiet(self):
        proc = self.m.add_process('foo', 'ruby server.rb', quiet=True)
        assert proc.quiet

    def test_add_process_name_must_be_unique(self):
        self.m.add_process('foo', 'ruby server.rb')
        with pytest.raises(AssertionError):
            self.m.add_process('foo', 'another command')

    def test_add_process_sets_cwd(self):
        proc = self.m.add_process('foo', 'ruby server.rb', cwd='foo-dir')
        assert proc.cwd == 'foo-dir'

    def test_loop_with_empty_manager_returns_immediately(self):
        self.m.loop()

    def test_loop_calls_process_run(self):
        self.run_history('one')
        evts = self.h.find_events(type='run')
        assert len(evts) == 1
        assert evts[0]['name'] == 'foo'
        assert evts[0]['events_passed']

    def test_printer_receives_messages_in_correct_order(self):
        self.run_history('one')
        self.p.fetch_lines()
        assert self.p.lines_local[0].data == 'foo started (pid=123)\n'
        assert self.p.lines_local[1].data == b'hello, world!\n'
        assert self.p.lines_local[2].data == 'foo stopped (rc=0)\n'

    def test_printer_receives_lines_multi_process(self):
        self.run_history('two')
        l1 = self.p.find_line(b'process one\n')
        l2 = self.p.find_line(b'process two\n')
        assert l1.name == 'foo'
        assert l2.name == 'bar'

    def test_returncode_set_by_first_exiting_process(self):
        self.run_history('returncode')
        assert self.h.manager_returncode == 456

    def test_printer_receives_lines_after_stop(self):
        self.run_history('output_after_stop')
        assert self.p.got_line(b'fishmongers\n')
        assert self.p.got_line(b'butchers\n')
