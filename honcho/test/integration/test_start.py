import textwrap
import sys
from ..helpers import TestCase
from ..helpers import TestEnv


python_bin = sys.executable

script = textwrap.dedent("""
    from __future__ import print_function
    import os
    import sys
    print(os.environ.get("ANIMAL", "elephant"))
    print("error output", file=sys.stderr)
""")


class TestStart(TestCase):
    def test_start(self):
        files = {
            'Procfile': 'foo: {0} test.py'.format(python_bin),
            'test.py': script,
        }

        with TestEnv(files) as env:
            ret, out, err = env.run_honcho(['start'])

        self.assertEqual(ret, 0)
        self.assertIn('elephant', out)
        self.assertIn('error output', out)

    def test_start_env(self):
        files = {
            '.env': 'ANIMAL=giraffe',
            'Procfile': 'foo: {0} test.py'.format(python_bin),
            'test.py': script,
        }

        with TestEnv(files) as env:
            ret, out, err = env.run_honcho(['start'])

        self.assertIn('giraffe', out)

    def test_start_returncode(self):
        files = {
            'Procfile': 'foo: {0} test.py'.format(python_bin),
            'test.py': 'import sys; sys.exit(42)',
        }

        with TestEnv(files) as env:
            ret, out, err = env.run_honcho(['start'])

        self.assertEqual(ret, 42)
