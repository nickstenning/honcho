import sys
import textwrap

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


class TestRun(TestCase):
    def test_run(self):
        with TestEnv({'test.py': script}) as env:
            ret, out, err = env.run_honcho(['run', python_bin, 'test.py'])

        self.assertEqual(ret, 0)
        self.assertEqual(out, 'elephant\n')
        self.assertEqual(err, 'error output\n')

    def test_run_env(self):
        with TestEnv({'.env': 'ANIMAL=giraffe', 'test.py': script}) as env:
            ret, out, err = env.run_honcho(['run', python_bin, 'test.py'])

        self.assertEqual(ret, 0)
        self.assertEqual(out, 'giraffe\n')

    def test_run_args_before_command(self):
        # Regression test for #122 -- ensure that common args can be given
        # before the subcommand.
        with TestEnv({'.env.x': 'ANIMAL=giraffe', 'test.py': script}) as env:
            ret, out, err = env.run_honcho(['-e', '.env.x',
                                            'run', python_bin, 'test.py'])

        self.assertEqual(ret, 0)
        self.assertEqual(out, 'giraffe\n')
