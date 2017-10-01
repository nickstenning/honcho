import os
import shutil
import tempfile
import time
import subprocess
from subprocess import Popen, PIPE

import pytest


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

    def run_honcho(self, args, respawn=False):
        cwd = os.getcwd()
        os.chdir(self.root)

        cmd = ['honcho']
        cmd.extend(args)

        if respawn:
            cmd.append('--respawn')

        # The below is mostly copy-pasted from subprocess.py's check_output (to
        # support python 2.6)
        process = Popen(cmd, stdout=PIPE, stderr=PIPE, universal_newlines=True)

        if respawn:
            time.sleep(1)
            process.send_signal(subprocess.signal.SIGTERM)

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
