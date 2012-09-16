from honcho.process import ProcessManager
from ..helpers import *


class TestProcessManager(object):

    @patch('honcho.process.Process')
    def test_add_processes(self, process_mock):
        pm = ProcessManager()
        pm.add_process('foo', 'ruby server.rb')
        pm.add_process('bar', 'python worker.py')

        expected = [call('ruby server.rb', name='foo'), call('python worker.py', name='bar')]

        assert_equal(process_mock.mock_calls, expected)
