import os
import shutil
import subprocess
import tempfile
from subprocess import PIPE

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

    def run_honcho(self, args):
        result = subprocess.run(
            ['honcho', *args],
            cwd=self.root,
            stdout=PIPE,
            stderr=PIPE,
            universal_newlines=True)

        return result.returncode, result.stdout, result.stderr

    def run(self, *args, **kwargs):
        options = {
            'cwd': self.root,
            'stdout': PIPE,
            'stderr': PIPE,
            'universal_newlines': True,
        }
        options.update(kwargs)

        return subprocess.run(*args, **options)


@pytest.fixture
def testenv(request):
    env = TestEnv(request.param)
    env.setup()
    request.addfinalizer(env.cleanup)
    return env
