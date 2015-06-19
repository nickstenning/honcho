import os, re

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

    def test_export_upstart_environment(self):
        with TestEnv(files) as env:
            env_path = os.path.join(env.root, '.env')

            with open(env_path, 'w') as file:
                # Add four environment variables to configuration.
                file.write('\n'.join(('A=a', 'B="b"', 'C=c c', 'D="d d"')))

            ret, out, err = env.run_honcho([
                'export',
                'upstart',
                env.path('elephant'),
                '-e', env_path,
                '-a', 'trunk',
            ])

            self.assertEqual(ret, 0)
            
            with open(env.path('elephant', 'trunk-web-1.conf')) as file:
                content = file.read()
                
                self.assertTrue(re.search(r'\bA=a\b', content), 'A should be "a"')
                self.assertTrue(re.search(r'\bB=b\b', content), 'B should be "b"')
                self.assertFalse(re.search(r'\bC=cc\b', content), 'C should be correctly-quoted "c c"')
                self.assertFalse(re.search(r"'cd [^']+\bexport D='d d';[^']+'", content), 'D should be correctly-quoted "d d"')
