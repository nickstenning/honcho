from ..helpers import TestCase
from ..helpers import get_honcho_output

from honcho import compat


class TestEnv(TestCase):

    def test_env_start(self):
        procfile = 'Procfile.envwin' if compat.ON_WINDOWS else 'Procfile.env'
        ret, out, err = get_honcho_output(['-f', procfile, 'start'])

        self.assertEqual(ret, 0)

        self.assertRegexpMatches(out, r'animals\.1 \| (....)?I like giraffes')

    def test_env_run(self):
        if compat.ON_WINDOWS:
            command = ['run', 'cmd', '/c', 'echo', '%TEST_ANIMAL%']
        else:
            command = ['run', 'sh', '-c', 'echo $TEST_ANIMAL']
        ret, out, err = get_honcho_output(command)

        self.assertEqual(ret, 0)
        self.assertEqual(out, 'giraffe\n')

    def test_env_quoted(self):
        procfile = 'Procfile.envwin_shlex' if compat.ON_WINDOWS else 'Procfile.env_shlex'
        ret, out, err = get_honcho_output(['-f', procfile, '-e', '.env_shlex', 'start'])

        self.assertEqual(ret, 0)

        self.assertRegexpMatches(out, r'animals\.1 \| (....)?I like "lion"s and also "tiger"s')
