import time
from threading import Thread

from ..helpers import TestCase
from honcho.process import ProcessManager


class FakePrinter(object):

    def __init__(self, output=None, name=None, **kwargs):
        self.name = name
        self.data = []

    def write(self, string):
        self.data.append(string)

    def last_write(self):
        return self.data[-1]


class FakeOutput(object):
    """
    FakeOutput accepts a set of lines to emit in response to a call to
    #readline(), after which it will emit b''.
    """

    def __init__(self, lines=None, attached_process=None):
        self.closed = False
        self.lines = lines if lines is not None else []
        self.attached_process = attached_process

    def readline(self):
        try:
            return self.lines.pop(0)
        except IndexError:
            if self.attached_process is not None:
                self.attached_process._stop()
            return b''

    def close(self):
        self.closed = True


class FakeBlockingOutput(FakeOutput):

    def readline(self):
        while not self.closed:
            time.sleep(10)


class FakeProcess(object):

    def __init__(self, command, name=None, quiet=False):
        self.command = command
        self.name = name
        self.quiet = quiet
        self.reader = None
        self.printer = None
        self.dead = False
        self.pid = 123
        self.returncode = 0

        self._running = True
        self._terminated = False
        self._killed = False

    def poll(self):
        if self._running:
            return None
        else:
            return self.returncode

    def terminate(self):
        self._terminated = True
        self._running = False

    def kill(self):
        self._killed = True
        self._running = False

    # Beyond here are helper methods for managing the process in the tests.
    def _stop(self):
        self._running = False


class TestProcessManager(TestCase):

    def test_add_process_creates_process(self):
        pm = ProcessManager(process=FakeProcess)
        proc = pm.add_process('foo', 'ruby server.rb')
        self.assertEqual('foo', proc.name)
        self.assertEqual('ruby server.rb', proc.command)
        self.assertFalse(proc.quiet)

    def test_process_printer_is_set(self):
        pm = ProcessManager(process=FakeProcess, printer=FakePrinter)
        proc = pm.add_process('foo', 'ruby server.rb')
        proc.stdout = FakeOutput(attached_process=proc)
        pm.loop()
        self.assertTrue(proc.printer is not None)

    def test_process_printer_receives_started_with_pid(self):
        pm = ProcessManager(process=FakeProcess, printer=FakePrinter)
        proc = pm.add_process('foo', 'ruby server.rb')
        proc.pid = 345
        proc.stdout = FakeOutput(attached_process=proc)
        pm.loop()
        self.assertEqual("started with pid 345\n", proc.printer.data[0])

    def test_process_printer_receives_output_lines(self):
        pm = ProcessManager(process=FakeProcess, printer=FakePrinter)
        proc = pm.add_process('foo', 'ruby server.rb')
        proc.pid = 345
        proc.stdout = FakeOutput(attached_process=proc)
        proc.stdout.lines = [b'hello\n', b'world\n']
        pm.loop()
        self.assertIn("hello\n", proc.printer.data)
        self.assertIn("world\n", proc.printer.data)

    def test_process_printer_appends_missing_newlines(self):
        pm = ProcessManager(process=FakeProcess, printer=FakePrinter)
        proc = pm.add_process('foo', 'ruby server.rb')
        proc.stdout = FakeOutput(attached_process=proc)
        proc.stdout.lines = [b'hello', b'world']
        pm.loop()
        self.assertIn("hello\n", proc.printer.data)
        self.assertIn("world\n", proc.printer.data)

    def test_process_printer_doesnt_print_quiet_processes(self):
        pm = ProcessManager(process=FakeProcess, printer=FakePrinter)
        proc = pm.add_process('foo', 'ruby server.rb', quiet=True)
        proc.stdout = FakeOutput(attached_process=proc)
        proc.stdout.lines = [b'hello\n', b'world\n']
        pm.loop()
        self.assertNotIn("hello\n", proc.printer.data)
        self.assertNotIn("world\n", proc.printer.data)

    def test_process_printer_handles_bad_utf8(self):
        pm = ProcessManager(process=FakeProcess, printer=FakePrinter)
        proc = pm.add_process('foo', 'ruby server.rb')
        proc.stdout = FakeOutput(attached_process=proc)
        proc.stdout.lines = [b'hello\n', b'\xfe\xff', b'world\n']
        pm.loop()
        self.assertIn("hello\n", proc.printer.data)
        self.assertIn("world\n", proc.printer.data)
        self.assertIn(
            "UnicodeDecodeError while decoding line from process foo\n",
            pm.system_printer.data)

    def test_process_printer_receives_process_terminated(self):
        pm = ProcessManager(process=FakeProcess, printer=FakePrinter)
        proc = pm.add_process('foo', 'ruby server.rb')
        proc.stdout = FakeOutput(attached_process=proc)
        pm.loop()
        self.assertEqual("process terminated\n", proc.printer.data[1])

    def test_process_stdout_is_closed(self):
        pm = ProcessManager(process=FakeProcess, printer=FakePrinter)
        proc = pm.add_process('foo', 'ruby server.rb')
        proc.stdout = FakeOutput(attached_process=proc)
        pm.loop()
        self.assertTrue(proc.stdout.closed)

    def test_processmanager_returncode_set_by_exiting_process(self):
        pm = ProcessManager(process=FakeProcess, printer=FakePrinter)
        proc = pm.add_process('foo', 'ruby server.rb')
        proc.stdout = FakeOutput(attached_process=proc)
        proc.returncode = 123
        pm.loop()
        self.assertEqual(123, pm.returncode)

    def test_processmanager_terminate_terminates_processes(self):
        pm = ProcessManager(process=FakeProcess, printer=FakePrinter)
        proc = pm.add_process('foo', 'ruby server.rb')
        proc.stdout = FakeBlockingOutput()

        def _terminate(manager):
            manager.terminate(kill_fallback=False)

        t = Thread(target=_terminate, args=(pm,))
        t.start()

        pm.loop()

        t.join()
        self.assertTrue(proc._terminated)
