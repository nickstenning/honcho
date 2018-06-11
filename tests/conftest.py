import os
import shutil
import sys
import tempfile
from subprocess import Popen, PIPE

import pytest

RUN_AS_PYTHON_PACKAGE = 'package'
RUN_AS_PYTHON_ENTRYPOINT = 'entrypoint'


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

    def run_honcho(self, args, runner=RUN_AS_PYTHON_ENTRYPOINT):
        if runner == RUN_AS_PYTHON_ENTRYPOINT:
            return self._run_honcho(args, cmd=['honcho'])
        elif runner == RUN_AS_PYTHON_PACKAGE:
            return self._run_honcho(args, cmd=[sys.executable, '-m', 'honcho'])

        raise NotImplementedError('Cannot run honcho as %r.' % (runner, ))

    def _run_honcho(self, args, cmd):
        cwd = os.getcwd()
        os.chdir(self.root)

        cmd.extend(args)

        # The below is mostly copy-pasted from subprocess.py's check_output (to
        # support python 2.6)
        process = Popen(cmd, stdout=PIPE, stderr=PIPE, universal_newlines=True)
        output, error = process.communicate()
        retcode = process.returncode

        os.chdir(cwd)

        return retcode, output, error


@pytest.fixture
def testenv(request):
    env = TestEnv(request.param)
    env.setup()
    request.addfinalizer(env.cleanup)
    return env
