import os
from ..helpers import TestCase
from ..helpers import get_honcho_output
from honcho import compat


class TestPorts(TestCase):

    def test_proctype_increment(self):
        procfile = 'Procfile.portswin' if compat.ON_WINDOWS else 'Procfile.ports'
        ret, out, err = get_honcho_output(['-f', procfile, 'start'])

        self.assertEqual(ret, 0)

        self.assertRegexpMatches(out, r'web\.1    \| (....)?PORT=5000')
        self.assertRegexpMatches(out, r'worker\.1 \| (....)?PORT=5100')
        self.assertRegexpMatches(out, r'redis\.1  \| (....)?PORT=5200')
        self.assertRegexpMatches(out, r'es\.1     \| (....)?PORT=5300')

    def test_concurrency_increment(self):
        procfile = 'Procfile.portswin' if compat.ON_WINDOWS else 'Procfile.ports'
        ret, out, err = get_honcho_output(['-f', procfile, 'start', '-c', 'web=2,worker=3'])

        self.assertEqual(ret, 0)

        self.assertRegexpMatches(out, r'web\.1    \| (....)?PORT=5000')
        self.assertRegexpMatches(out, r'web\.2    \| (....)?PORT=5001')
        self.assertRegexpMatches(out, r'worker\.1 \| (....)?PORT=5100')
        self.assertRegexpMatches(out, r'worker\.2 \| (....)?PORT=5101')
        self.assertRegexpMatches(out, r'worker\.3 \| (....)?PORT=5102')
        self.assertRegexpMatches(out, r'redis\.1  \| (....)?PORT=5200')
        self.assertRegexpMatches(out, r'es\.1     \| (....)?PORT=5300')

    def test_get_port_from_dot_env(self):
        procfile = 'Procfile.portswin' if compat.ON_WINDOWS else 'Procfile.ports'
        ret, out, err = get_honcho_output(['-f', procfile, '-e', '.env_port', 'start'])

        self.assertEqual(ret, 0)

        self.assertRegexpMatches(out, r'web\.1    \| (....)?PORT=8000')

    def test_get_port_from_env(self):
        os.environ['PORT'] = '3000'
        procfile = 'Procfile.portswin' if compat.ON_WINDOWS else 'Procfile.ports'
        ret, out, err = get_honcho_output(['-f', procfile, 'start'])
        del os.environ['PORT']

        self.assertEqual(ret, 0)

        self.assertRegexpMatches(out, r'web\.1    \| (....)?PORT=3000')
