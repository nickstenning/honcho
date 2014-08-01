import sys
from ..helpers import TestCase
from ..helpers import get_honcho_output

from honcho import compat


class TestRun(TestCase):

    def test_run_quoting(self):
        # 'python' is not always in the path on all test os
        # in particular on Windows, this is not the case
        python = sys.executable
        ret, out, err = get_honcho_output(['run', python, '-c',
                                           'print("hello world")'])

        self.assertEqual(ret, 0)
        self.assertEqual(out, 'hello world\n')

    def test_run_captures_all_arguments(self):
        if compat.ON_WINDOWS:
            return
        command = ['run', 'env', '-i', 'A=B']
        ret, out, err = get_honcho_output(command)
        self.assertEqual(ret, 0)
        self.assertEqual(out.strip(), "A=B")

    def test_run_captures_all_arguments_windows(self):
        # note: this is not the same exact test as on Posix
        # but this captures the gist of the intention
        if not compat.ON_WINDOWS:
            return
        command = ['run', 'cmd', '/a', '/e:on', '/c', 'cd', '&', 'set']
        ret, out, err = get_honcho_output(command)
        self.assertEqual(ret, 0)
        self.assertTrue("honcho" in out)
        self.assertTrue("HOMEDRIVE" in out)

    def test_run_keeps_stderr_and_stdout_separate(self):
        ret, out, err = get_honcho_output(['run', 'python', 'simple.py'])

        self.assertEqual(ret, 0)
        self.assertEqual(out, 'normal output\n')
        self.assertEqual(err, 'error output\n')
