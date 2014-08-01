from ..helpers import TestCase
from mock import call, patch
from honcho.process import ProcessManager


class TestProcessManager(TestCase):

    @patch('honcho.process.Process')
    def test_add_processes(self, process_mock):
        pm = ProcessManager()
        pm.add_process('foo', 'ruby server.rb')
        pm.add_process('bar', 'python worker.py')

        expected = [call('ruby server.rb', name='foo', quiet=False),
                    call('python worker.py', name='bar', quiet=False)]

        self.assertEqual(process_mock.mock_calls, expected)
