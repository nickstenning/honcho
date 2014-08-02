from collections import namedtuple
import time
from threading import Thread
import subprocess

from ..helpers import TestCase
from honcho.process import Process
from honcho.process import ProcessManager
from honcho.process import SYSTEM_PRINTER_NAME


class FakePopen(object):

    POLL_RESULT = object()
    WAIT_RESULT = object()

    def __init__(self, args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.stdout = object()
        self.stderr = object()
        self.stdin = object()
        self.pid = 0x42
        self.returncode = 0
        self.terminated = False
        self.killed = False

    def poll(self):
        return self.POLL_RESULT

    def wait(self):
        return self.WAIT_RESULT

    def terminate(self):
        self.terminated = True

    def kill(self):
        self.killed = True


PrinterLine = namedtuple('PrinterLine', 'index string name width colour')


class FakePrinter(object):

    def __init__(self, output=None, width=0):
        self.lines = []
        self.index = 0
        self.width = width

    def write(self, string, name="", colour=None):
        self.lines.append(PrinterLine(self.index, string, name, self.width, colour))
        self.index += 1

    def got_line(self, string):
        return self.find_line(string) is not None

    def find_line(self, string):
        for line in self.lines:
            if line.string == string:
                return line
        return None

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


class TestProcess(TestCase):

    def test_command(self):
        proc = Process('echo 123', popen=FakePopen)
        self.assertEqual('echo 123', proc.proc.args)

    def test_default_stdout(self):
        proc = Process('echo 123', popen=FakePopen)
        self.assertEqual(subprocess.PIPE, proc.proc.kwargs['stdout'])

    def test_default_stderr(self):
        proc = Process('echo 123', popen=FakePopen)
        self.assertEqual(subprocess.STDOUT, proc.proc.kwargs['stderr'])

    def test_default_shell(self):
        proc = Process('echo 123', popen=FakePopen)
        self.assertTrue(proc.proc.kwargs['shell'])

    def test_default_bufsize(self):
        proc = Process('echo 123', popen=FakePopen)
        self.assertEqual(1, proc.proc.kwargs['bufsize'])

    def test_quiet(self):
        proc = Process('echo 123', popen=FakePopen)
        self.assertFalse(proc.quiet)

    def test_quiet_name(self):
        proc = Process('echo 123', name='foo', quiet=True, popen=FakePopen)
        self.assertEqual('foo (quiet)', proc.name)

    def test_poll(self):
        proc = Process('echo 123', popen=FakePopen)
        self.assertEqual(FakePopen.POLL_RESULT, proc.poll())

    def test_kill(self):
        proc = Process('echo 123', popen=FakePopen)
        proc.kill()
        self.assertTrue(proc.proc.killed)

    def test_terminate(self):
        proc = Process('echo 123', popen=FakePopen)
        proc.terminate()
        self.assertTrue(proc.proc.terminated)

    def test_wait(self):
        proc = Process('echo 123', popen=FakePopen)
        self.assertEqual(FakePopen.WAIT_RESULT, proc.wait())

    def test_pid(self):
        proc = Process('echo 123', popen=FakePopen)
        self.assertEqual(proc.proc.pid, proc.pid)

    def test_returncode(self):
        proc = Process('echo 123', popen=FakePopen)
        self.assertEqual(proc.proc.returncode, proc.returncode)

    def test_stdout_stderr_stdin(self):
        proc = Process('echo 123', popen=FakePopen)
        self.assertEqual(proc.proc.stdout, proc.stdout)
        self.assertEqual(proc.proc.stderr, proc.stderr)
        self.assertEqual(proc.proc.stdin, proc.stdin)


class TestProcessManager(TestCase):

    def test_add_process_creates_process(self):
        pm = ProcessManager(process=FakeProcess)
        proc = pm.add_process('foo', 'ruby server.rb')
        self.assertEqual('foo', proc.name)
        self.assertEqual('ruby server.rb', proc.command)
        self.assertFalse(proc.quiet)

    def test_sets_default_printer_width(self):
        printer = FakePrinter()
        ProcessManager(process=FakeProcess, printer=printer)
        self.assertEqual(len(SYSTEM_PRINTER_NAME), printer.width)

    def test_add_process_updates_printer_width(self):
        printer = FakePrinter()
        pm = ProcessManager(process=FakeProcess, printer=printer)
        pm.add_process('interesting', 'ruby server.rb')
        self.assertEqual(len('interesting'), printer.width)

    def test_printer_receives_started_with_pid(self):
        printer = FakePrinter()
        pm = ProcessManager(process=FakeProcess, printer=printer)
        proc = pm.add_process('foo', 'ruby server.rb')
        proc.pid = 345
        proc.stdout = FakeOutput(attached_process=proc)
        pm.loop()
        self.assertTrue(printer.got_line("started with pid 345\n"))

    def test_printer_receives_output_lines(self):
        printer = FakePrinter()
        pm = ProcessManager(process=FakeProcess, printer=printer)
        proc = pm.add_process('foo', 'ruby server.rb')
        proc.stdout = FakeOutput(attached_process=proc)
        proc.stdout.lines = [b'hello\n', b'world\n']
        pm.loop()
        self.assertTrue(printer.got_line("hello\n"))
        self.assertTrue(printer.got_line("world\n"))

    def test_printer_receives_output_lines_in_order(self):
        printer = FakePrinter()
        pm = ProcessManager(process=FakeProcess, printer=printer)
        p1 = pm.add_process('foo', 'ruby server.rb')
        p1.stdout = FakeOutput(attached_process=p1)
        p1.stdout.lines = [b'hello\n', b'world\n', b'giraffe\n']
        p2 = pm.add_process('bar', 'python worker.py')
        p2.stdout = FakeOutput(attached_process=p2)
        p2.stdout.lines = [b'donkeys\n', b'eat\n', b'grass\n']
        pm.loop()
        p1l1 = printer.find_line("hello\n")
        p1l2 = printer.find_line("world\n")
        p1l3 = printer.find_line("giraffe\n")
        p2l1 = printer.find_line("donkeys\n")
        p2l2 = printer.find_line("eat\n")
        p2l3 = printer.find_line("grass\n")
        self.assertTrue(p1l1.index < p1l2.index < p1l3.index)
        self.assertTrue(p2l1.index < p2l2.index < p2l3.index)

    def test_processes_have_different_colours(self):
        printer = FakePrinter()
        pm = ProcessManager(process=FakeProcess, printer=printer)
        p1 = pm.add_process('foo', 'ruby server.rb')
        p1.stdout = FakeOutput(attached_process=p1)
        p1.stdout.lines = [b'elephants\n']
        p2 = pm.add_process('bar', 'python worker.py')
        p2.stdout = FakeOutput(attached_process=p2)
        p2.stdout.lines = [b'anteaters\n']
        pm.loop()
        p1l1 = printer.find_line("elephants\n")
        p2l1 = printer.find_line("anteaters\n")
        self.assertNotEqual(p1l1.colour, p2l1.colour)

    def test_process_colours_are_consistent(self):
        printer = FakePrinter()
        pm = ProcessManager(process=FakeProcess, printer=printer)
        p1 = pm.add_process('foo', 'ruby server.rb')
        p1.stdout = FakeOutput(attached_process=p1)
        p1.stdout.lines = [b'hello\n', b'world\n']
        p2 = pm.add_process('bar', 'python worker.py')
        p2.stdout = FakeOutput(attached_process=p2)
        p2.stdout.lines = [b'donkeys\n', b'giraffes\n']
        pm.loop()
        p1l1 = printer.find_line("hello\n")
        p1l2 = printer.find_line("world\n")
        p2l1 = printer.find_line("donkeys\n")
        p2l2 = printer.find_line("giraffes\n")
        self.assertEqual(p1l1.colour, p1l2.colour)
        self.assertEqual(p2l1.colour, p2l2.colour)

    def test_doesnt_print_quiet_processes(self):
        printer = FakePrinter()
        pm = ProcessManager(process=FakeProcess, printer=printer)
        proc = pm.add_process('foo', 'ruby server.rb', quiet=True)
        proc.stdout = FakeOutput(attached_process=proc)
        proc.stdout.lines = [b'hello\n', b'world\n']
        pm.loop()
        self.assertFalse(printer.got_line("hello\n"))
        self.assertFalse(printer.got_line("hello\n"))

    def test_handles_bad_utf8(self):
        printer = FakePrinter()
        pm = ProcessManager(process=FakeProcess, printer=printer)
        proc = pm.add_process('foo', 'ruby server.rb')
        proc.stdout = FakeOutput(attached_process=proc)
        proc.stdout.lines = [b'hello\n', b'\xfe\xff', b'world\n']
        pm.loop()
        self.assertTrue(printer.got_line("hello\n"))
        self.assertTrue(printer.got_line("world\n"))
        self.assertTrue(printer.got_line(
            "UnicodeDecodeError while decoding line from process foo\n"))

    def test_printer_receives_process_terminated(self):
        printer = FakePrinter()
        pm = ProcessManager(process=FakeProcess, printer=printer)
        proc = pm.add_process('foo', 'ruby server.rb')
        proc.stdout = FakeOutput(attached_process=proc)
        pm.loop()
        self.assertTrue(printer.got_line("process terminated\n"))

    def test_process_stdout_is_closed(self):
        printer = FakePrinter()
        pm = ProcessManager(process=FakeProcess, printer=printer)
        proc = pm.add_process('foo', 'ruby server.rb')
        proc.stdout = FakeOutput(attached_process=proc)
        pm.loop()
        self.assertTrue(proc.stdout.closed)

    def test_processmanager_returncode_set_by_exiting_process(self):
        printer = FakePrinter()
        pm = ProcessManager(process=FakeProcess, printer=printer)
        proc = pm.add_process('foo', 'ruby server.rb')
        proc.stdout = FakeOutput(attached_process=proc)
        proc.returncode = 123
        pm.loop()
        self.assertEqual(123, pm.returncode)

    def test_processmanager_terminate_terminates_processes(self):
        printer = FakePrinter()
        pm = ProcessManager(process=FakeProcess, printer=printer)
        proc = pm.add_process('foo', 'ruby server.rb')
        proc.stdout = FakeBlockingOutput()

        def _terminate(manager):
            manager.terminate(kill_fallback=False)

        t = Thread(target=_terminate, args=(pm,))
        t.start()

        pm.loop()

        t.join()
        self.assertTrue(proc._terminated)
