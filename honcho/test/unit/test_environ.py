import textwrap
from ..helpers import TestCase

from honcho import environ
from honcho import compat

ENVFILE_FIXTURES = [
    [
        """
        FOO=bar
        """,
        {'FOO': 'bar'}
    ],
    [
        """
        FOO=bar
        BAZ=qux
        """,
        {'FOO': 'bar', 'BAZ': 'qux'}
    ],
    [
        # No newline at EOF
        """
        FOO=bar""",
        {'FOO': 'bar'}
    ],
    [
        # Comments
        """
        #commented: command
        """,
        {}
    ],
    [
        # Invalid characters
        """
        -foo=command
        """,
        {}
    ],
    [
        # Single quoted
        """
        MYVAR='hello"world'
        """,
        {'MYVAR': 'hello"world'}
    ],
    [
        # Double quoted
        """
        MYVAR="hello'world"
        """,
        {'MYVAR': "hello'world"}
    ],
]

PROCFILE_FIXTURES = [
    [
        # Simple
        """
        web: command
        """,
        {'web': 'command'}
    ],
    [
        # Simple 2
        """
        foo: python foo.py
        bar: python bar.py
        """,
        {'foo': 'python foo.py', 'bar': 'python bar.py'}
    ],
    [
        # No newline at EOF
        """
        web: command""",
        {'web': 'command'}
    ],
    [
        # Comments
        """
        #commented: command
        """,
        {}
    ],
    [
        # Invalid characters
        """
        -foo: command
        """,
        {}
    ],
    [
        # Shell metacharacters
        """
        web: sh -c "echo $FOOBAR" >/dev/null 2>&1
        """,
        {'web': 'sh -c "echo $FOOBAR" >/dev/null 2>&1'}
    ],
]


class TestEnviron(TestCase):
    def test_environ_parse(self):
        for content, commands in ENVFILE_FIXTURES:
            content = textwrap.dedent(content)
            result = environ.parse(content)
            self.assertEqual(result, commands)


class TestProcfileParse(TestCase):

    def test_parse_procfiles(self):
        for content, processes in PROCFILE_FIXTURES:
            content = textwrap.dedent(content)
            p = environ.parse_procfile(content)
            self.assertEqual(p.processes, processes)

    def test_procfile_ordered(self):
        content = textwrap.dedent("""
        one: onecommand
        two: twocommand
        three: twocommand
        four: fourcommand
        """)

        p = environ.parse_procfile(content)
        order = [k for k in p.processes]
        self.assertEqual(['one', 'two', 'three', 'four'], order)


class TestProcfile(TestCase):

    def test_init(self):
        p = environ.Procfile()
        self.assertEqual(0, len(p.processes))

    def test_add_process(self):
        p = environ.Procfile()
        p.add_process('foo', 'echo 123')
        self.assertEqual('echo 123', p.processes['foo'])

    def test_add_process_ensures_unique_name(self):
        p = environ.Procfile()
        p.add_process('foo', 'echo 123')
        self.assertRaises(AssertionError, p.add_process, 'foo', 'echo 123')
