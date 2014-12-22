import textwrap

from ..helpers import TestCase
from ..helpers import TestEnv


class TestCheck(TestCase):
    def test_check(self):
        files = {
            'Procfile': textwrap.dedent("""
                foo: python web.py
                bar: ruby worker.rb
                baz: node socket.js
            """)
        }

        with TestEnv(files) as env:
            ret, out, err = env.run_honcho(['check'])

        self.assertEqual(ret, 0)
        self.assertIn('Valid procfile detected', err)
        self.assertIn('foo, bar, baz', err)
