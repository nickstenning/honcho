import os
import textwrap

from ..helpers import TestCase
from ..helpers import TestEnv

files = {
    'Procfile': "web: python web.py"
}


class TestExport(TestCase):
    def test_export_supervisord(self):
        with TestEnv(files) as env:
            ret, out, err = env.run_honcho([
                'export',
                'supervisord',
                env.path('giraffe'),
                '-a', 'neck',
            ])

            expected = env.path('giraffe', 'neck.conf')

            self.assertEqual(ret, 0)
            self.assertTrue(os.path.exists(expected))

    def test_export_upstart(self):
        with TestEnv(files) as env:
            ret, out, err = env.run_honcho([
                'export',
                'upstart',
                env.path('elephant'),
                '-a', 'trunk',
            ])

            self.assertEqual(ret, 0)
            for filename in ('trunk.conf',
                             'trunk-web.conf',
                             'trunk-web-1.conf'):
                expected = env.path('elephant', filename)
                self.assertTrue(os.path.exists(expected))
