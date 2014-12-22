import os
import shutil
import tempfile
import unittest
from subprocess import Popen, PIPE


class TestCase(unittest.TestCase):
    if not hasattr(unittest.TestCase, 'assertIn'):
        def assertIn(self, member, container, msg=None):  # noqa
                """Just like self.assertTrue(a in b), but with a nicer default message."""
                if member not in container:
                    standardMsg = '%s not found in %s' % (repr(member),  # noqa
                                                          repr(container))
                    self.fail(self._formatMessage(msg, standardMsg))


class TestEnv(object):
    def __init__(self, files=None):
        self.root = None
        self._files = files

    def cleanup(self):
        if self.root is not None:
            shutil.rmtree(self.root)
            self.root = None

    def setup(self):
        self.cleanup()

        self.root = tempfile.mkdtemp()
        if self._files is not None:
            for n, contents in self._files.items():
                with open(os.path.join(self.root, n), 'w') as fp:
                    fp.write(contents)

    def path(self, *args):
        return os.path.join(self.root, *args)

    def run_honcho(self, args):
        cwd = os.getcwd()
        os.chdir(self.root)

        cmd = ['honcho']
        cmd.extend(args)

        # The below is mostly copy-pasted from subprocess.py's check_output (to
        # support python 2.6)

        process = Popen(cmd, stdout=PIPE, stderr=PIPE, universal_newlines=True)
        output, error = process.communicate()
        retcode = process.returncode

        os.chdir(cwd)

        return retcode, output, error

    def __enter__(self):
        self.setup()
        return self

    def __exit__(self, *args):
        self.cleanup()

    def __del__(self):
        self.cleanup()
