from ..helpers import TestCase
from honcho.process import ProcessManager

process_instances = []


class FakeProcess(object):

    def __init__(self, command, name=None, quiet=False):
        self.command = command
        self.name = name
        self.quiet = quiet
        process_instances.append(self)


class TestProcessManager(TestCase):

    def test_add_processes(self):
        pm = ProcessManager(process=FakeProcess)
        pm.add_process('foo', 'ruby server.rb')
        pm.add_process('bar', 'python worker.py')

        self.assertEqual(2, len(process_instances))
        self.assertEqual('foo', process_instances[0].name)
        self.assertEqual('ruby server.rb', process_instances[0].command)
        self.assertFalse(process_instances[0].quiet)
        self.assertEqual('bar', process_instances[1].name)
        self.assertEqual('python worker.py', process_instances[1].command)
        self.assertFalse(process_instances[1].quiet)
